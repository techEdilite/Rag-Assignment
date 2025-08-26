import re
import os
from datetime import datetime, timedelta
from google.cloud import bigquery
import psycopg2

from bigQueryhandler import SimpleSQLGenerator

# SQLAlchemy imports
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Date, Float, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import select, func, and_, or_
from sqlalchemy.dialects import postgresql, mysql, sqlite
from sqlalchemy.inspection import inspect

# Create declarative base for ORM models
Base = declarative_base()

# =============================================================================
# FIXED ORM MODEL - NO ID COLUMN
# =============================================================================

class CarSalesData(Base):
    """
    FINAL CORRECTED ORM model - NO ID column since your table doesn't have one
    Using composite primary key from existing columns
    """
    __tablename__ = 'car_sales'
    
    # ❌ COMPLETELY REMOVE id column - it doesn't exist in your table
    # id = Column(Integer, primary_key=True, autoincrement=True)  # REMOVED
    
    # ✅ YOUR ACTUAL COLUMNS - Use composite primary key
    date = Column(Date, primary_key=True)
    salesperson = Column(String(100), primary_key=True)
    customer_name = Column(String(100), primary_key=True)
    car_make = Column(String(50))
    car_model = Column(String(50))
    car_year = Column(Integer)
    sale_price = Column(Float)
    commission_rate = Column(Float)
    commission_earned = Column(Float)
    
    def __repr__(self):
        return f"<CarSale(make='{self.car_make}', model='{self.car_model}', price={self.sale_price})>"

class SmartQuerySystemWithSQLAlchemy:
    def __init__(self, psql_config, bigquery_credentials_path, project_id, dataset_id, table_id):
        self.psql_config = psql_config
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.table_id = table_id

        self.simple_sql_generatorq = SimpleSQLGenerator(
            ""
        )
        
        # Set up BigQuery client
        self.bq_client = self._setup_bigquery_client(bigquery_credentials_path, project_id)
        self.bq_table_ref = f"`{project_id}.{dataset_id}.{table_id}`"
        
        # SQLAlchemy Setup
        self.pg_engine = self._create_postgresql_engine(psql_config)
        self.SessionLocal = sessionmaker(bind=self.pg_engine)
        
        # Reflect existing database structure
        self.metadata = MetaData()
        self.metadata.reflect(bind=self.pg_engine)
        
        # ✅ CORRECTED: Try both possible table names - fix boolean issue
        self.car_sales_table = self.metadata.tables.get('car_sales')
        if self.car_sales_table is None:
            self.car_sales_table = self.metadata.tables.get('car_sales_data')
        
        # Create ORM session
        self.session = self.SessionLocal()
        
        # Keywords for routing
        self.bigquery_keywords = [
            'analytics', 'analysis', 'trend', 'trends', 'average', 'avg',
            'monthly', 'yearly', 'quarterly', 'last month', 'last year',
            'total sales', 'performance', 'growth', 'compare', 'comparison',
            'highest', 'lowest', 'top', 'bottom', 'rank', 'ranking',
            'commission', 'profit', 'revenue', 'summary', 'report'
        ]
        
        self.postgresql_keywords = [
            'find', 'show', 'get', 'specific', 'customer', 'record',
            'where', 'lookup', 'search', 'individual', 'single',
            'details', 'info', 'information'
        ]
        
        # Car brands and models
        self.car_brands = ['toyota', 'honda', 'ford', 'bmw', 'mercedes', 'audi', 'tesla', 'nissan', 'hyundai']
        self.car_models = ['corolla', 'camry', 'civic', 'accord', 'f150', 'mustang', 'model s', 'model 3', 'silverado']

    def _create_postgresql_engine(self, config):
        try:
            connection_string = (
                f"postgresql://{config['user']}:{config['password']}"
                f"@{config['host']}/{config['database']}"
            )
            
            engine = create_engine(
                connection_string,
                pool_size=10,
                max_overflow=20,
                pool_recycle=3600,
                echo=False
            )
            
            print(f"✅ SQLAlchemy engine created for PostgreSQL")
            return engine
            
        except Exception as e:
            print(f"❌ Failed to create SQLAlchemy engine: {e}")
            raise

    def _setup_bigquery_client(self, credentials_path, project_id):
        try:
            if credentials_path and os.path.exists(credentials_path):
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
                print(f"✅ Using BigQuery credentials from: {credentials_path}")
            
            client = bigquery.Client(project=project_id)
            print(f"✅ Connected to BigQuery project: {project_id}")
            
            try:
                dataset = client.get_dataset(self.dataset_id)
                print(f"✅ Dataset '{self.dataset_id}' accessible")
            except Exception as e:
                print(f"⚠️  Dataset access test failed: {e}")
            
            return client
            
        except Exception as e:
            print(f"❌ Failed to connect to BigQuery: {e}")
            raise

    def get_table_schema(self):
        print("🔍 Analyzing Database Schema with SQLAlchemy...")
        
        if self.car_sales_table is not None:
            print(f"📋 Table: {self.car_sales_table.name}")
            print("📋 Columns:")
            for column in self.car_sales_table.columns:
                print(f"   - {column.name}: {column.type} (Primary Key: {column.primary_key})")
        
        # Use ORM model inspection
        mapper = inspect(CarSalesData)
        print(f"\n🎯 ORM Model Columns:")
        for column in mapper.columns:
            print(f"   - {column.name}: {column.type}")

    def test_connections(self):
        print("🔍 Testing Database Connections...")
        print("=" * 50)
        
        # Test SQLAlchemy PostgreSQL connection
        try:
            # Method 1: Using SQLAlchemy Core with correct table name
            with self.pg_engine.connect() as connection:
                result = connection.execute(text("SELECT COUNT(*) FROM car_sales"))
                pg_count = result.scalar()
            print(f"✅ PostgreSQL (SQLAlchemy Core): {pg_count:,} records")
            
            # Method 2: Using SQLAlchemy ORM - COUNT(*) without specifying column
            try:
                # ✅ FIXED: Use func.count() without specifying non-existent id column
                orm_count = self.session.query(func.count()).select_from(CarSalesData).scalar()
                print(f"✅ PostgreSQL (SQLAlchemy ORM): {orm_count:,} records")
            except Exception as e:
                print(f"⚠️  ORM count method failed, trying alternative: {e}")
                # Alternative: count using existing column
                orm_count2 = self.session.query(func.count(CarSalesData.date)).scalar()
                print(f"✅ PostgreSQL (SQLAlchemy ORM Alternative): {orm_count2:,} records")
            
        except Exception as e:
            print(f"❌ PostgreSQL SQLAlchemy connection failed: {e}")
        
        # Test BigQuery connection
        try:
            query = f"SELECT COUNT(*) as count FROM {self.bq_table_ref}"
            results = self.bq_client.query(query)
            for row in results:
                bq_count = row.count
            print(f"✅ BigQuery: {bq_count:,} records in {self.table_id}")
        except Exception as e:
            print(f"❌ BigQuery connection failed: {e}")
        
        print("-" * 50)

    def process_user_query(self, user_input):
        print(f"🔍 Processing query: '{user_input}'")
        
        database = self._route_query(user_input)
        print(f"📍 Routing to: {database}")
        
        if database == "POSTGRESQL":
            query_result = self._convert_to_sqlalchemy_query(user_input)
        else:
            print("🔍 Converting to SQL...")
            query_result = self._convert_to_sql(user_input, database)
        
        if query_result.get('error'):
            return {
                'user_query': user_input,
                'routed_to': database,
                'error': query_result['error']
            }
        
        print(f"🛠 Generated Query: {query_result.get('sql') or query_result.get('orm_description')}")
        
        print(database)
        if database == "POSTGRESQL":
            print("🚀 Executing SQLAlchemy ORM Query... - = = =  =  =")
            execution_result = self._execute_sqlalchemy_query(query_result)
        else:
            print("🚀 Executing SQL... - = = =  =  =")
            execution_result = self._execute_query(query_result['sql'], database)
        
        return {
            'user_query': user_input,
            'routed_to': database,
            'generated_query': query_result.get('sql') or query_result.get('orm_description'),
            'explanation': query_result['explanation'],
            'results': execution_result
        }

    def _convert_to_sqlalchemy_query(self, user_input):
        user_lower = user_input.lower()
        
        try:
            if self._is_count_query(user_lower):
                return self._handle_count_query_sqlalchemy(user_lower)
            elif self._is_time_query(user_lower):
                return self._handle_time_query_sqlalchemy(user_lower)
            elif self._is_brand_model_query(user_lower):
                return self._handle_brand_model_query_sqlalchemy(user_lower)
            elif self._is_price_query(user_lower):
                return self._handle_price_query_sqlalchemy(user_lower)
            elif self._is_commission_query(user_lower):
                return self._handle_commission_query_sqlalchemy(user_lower)
            elif self._is_year_query(user_lower):
                return self._handle_year_query_sqlalchemy(user_lower)
            elif self._is_salesperson_query(user_lower):
                return self._handle_salesperson_query_sqlalchemy(user_lower)
            else:
                return {
                    'orm_query': None,
                    'explanation': None,
                    'error': "Try: 'how many toyota cars', 'sales by Mary Lawrence', 'cars from 2018', 'highest commission'"
                }
                
        except Exception as e:
            return {
                'orm_query': None,
                'explanation': None,
                'error': f"Error generating SQLAlchemy query: {str(e)}"
            }

    # =============================================================================
    # FIXED QUERY HANDLERS - NO ID COLUMN REFERENCES
    # =============================================================================

    def _handle_count_query_sqlalchemy(self, query):
        """FIXED: No id column references"""
        model_found = None
        brand_found = None
        
        for model in self.car_models:
            if model in query:
                model_found = model
                break
        
        for brand in self.car_brands:
            if brand in query:
                brand_found = brand
                break
        
        if model_found:
            # ✅ FIXED: Use func.count() without id column
            orm_query = self.session.query(func.count()).filter(
                CarSalesData.car_model.ilike(f'%{model_found}%')
            )
            explanation = f"Counting all {model_found} cars using SQLAlchemy ORM"
            orm_description = f"session.query(func.count()).filter(CarSalesData.car_model.ilike('%{model_found}%'))"
            
        elif brand_found:
            orm_query = self.session.query(func.count()).filter(
                CarSalesData.car_make.ilike(f'%{brand_found}%')
            )
            explanation = f"Counting all {brand_found} cars using SQLAlchemy ORM"
            orm_description = f"session.query(func.count()).filter(CarSalesData.car_make.ilike('%{brand_found}%'))"
            
        else:
            orm_query = self.session.query(func.count()).select_from(CarSalesData)
            explanation = "Counting all cars using SQLAlchemy ORM"
            orm_description = "session.query(func.count()).select_from(CarSalesData)"
        
        return {
            'orm_query': orm_query,
            'orm_description': orm_description,
            'explanation': explanation,
            'error': None
        }

    def _handle_time_query_sqlalchemy(self, query):
        """FIXED: No id column references"""
        if 'last month' in query:
            today = datetime.now()
            last_month = today.replace(day=1) - timedelta(days=1)
            last_month_start = last_month.replace(day=1)
            
            # ✅ FIXED: Use func.count() without id column
            orm_query = self.session.query(
                func.count().label('total_sales'),  # No id reference
                func.sum(CarSalesData.sale_price).label('total_revenue'),
                func.avg(CarSalesData.sale_price).label('avg_price'),
                func.sum(CarSalesData.commission_earned).label('total_commission')
            ).filter(
                and_(
                    CarSalesData.date >= last_month_start,
                    CarSalesData.date < today.replace(day=1)
                )
            )
            
            explanation = f"Sales data for last month"
            orm_description = f"session.query with date range filter for last month"
            
        elif 'this month' in query:
            today = datetime.now()
            month_start = today.replace(day=1)
            
            orm_query = self.session.query(
                func.count().label('total_sales'),  # No id reference
                func.sum(CarSalesData.sale_price).label('total_revenue'),
                func.avg(CarSalesData.sale_price).label('avg_price'),
                func.sum(CarSalesData.commission_earned).label('total_commission')
            ).filter(
                CarSalesData.date >= month_start
            )
            
            explanation = f"Sales data for this month"
            orm_description = f"session.query with this month filter"
        
        return {
            'orm_query': orm_query,
            'orm_description': orm_description,
            'explanation': explanation,
            'error': None
        }

    def _handle_brand_model_query_sqlalchemy(self, query):
        """Handle brand/model queries"""
        brand_found = None
        model_found = None
        
        for brand in self.car_brands:
            if brand in query:
                brand_found = brand
                break
        
        for model in self.car_models:
            if model in query:
                model_found = model
                break
        
        if model_found:
            orm_query = self.session.query(CarSalesData).filter(
                CarSalesData.car_model.ilike(f'%{model_found}%')
            ).limit(50)
            explanation = f"All {model_found} cars using SQLAlchemy ORM"
            orm_description = f"session.query(CarSalesData).filter(car_model.ilike('%{model_found}%'))"
            
        elif brand_found:
            orm_query = self.session.query(CarSalesData).filter(
                CarSalesData.car_make.ilike(f'%{brand_found}%')
            ).limit(50)
            explanation = f"All {brand_found} cars using SQLAlchemy ORM"
            orm_description = f"session.query(CarSalesData).filter(car_make.ilike('%{brand_found}%'))"
        
        return {
            'orm_query': orm_query,
            'orm_description': orm_description,
            'explanation': explanation,
            'error': None
        }

    def _handle_price_query_sqlalchemy(self, query):
        """Handle price queries"""
        numbers = re.findall(r'\d+', query)
        
        if numbers and 'under' in query:
            price_limit = int(numbers[0])
            orm_query = self.session.query(CarSalesData).filter(
                CarSalesData.sale_price < price_limit
            ).order_by(CarSalesData.sale_price).limit(50)
            
            explanation = f"Cars under ${price_limit:,}"
            orm_description = f"session.query(CarSalesData).filter(sale_price < {price_limit})"
            
        elif numbers and 'over' in query:
            price_limit = int(numbers[0])
            orm_query = self.session.query(CarSalesData).filter(
                CarSalesData.sale_price > price_limit
            ).order_by(CarSalesData.sale_price.desc()).limit(50)
            
            explanation = f"Cars over ${price_limit:,}"
            orm_description = f"session.query(CarSalesData).filter(sale_price > {price_limit})"
            
        else:
            orm_query = self.session.query(
                func.min(CarSalesData.sale_price).label('min_price'),
                func.max(CarSalesData.sale_price).label('max_price'),
                func.avg(CarSalesData.sale_price).label('avg_price')
            )
            explanation = "Price statistics"
            orm_description = "session.query with min, max, avg functions on sale_price"
        
        return {
            'orm_query': orm_query,
            'orm_description': orm_description,
            'explanation': explanation,
            'error': None
        }

    def _handle_commission_query_sqlalchemy(self, query):
        """Handle commission queries"""
        if 'highest' in query or 'higher' in query:
            orm_query = self.session.query(
                CarSalesData.car_make,
                CarSalesData.car_model,
                CarSalesData.sale_price,
                CarSalesData.commission_rate,
                CarSalesData.commission_earned
            ).filter(
                CarSalesData.commission_earned > self.session.query(func.avg(CarSalesData.commission_earned)).scalar()
            ).order_by(CarSalesData.commission_earned.desc()).limit(20)
            
            explanation = "Cars with above-average commission"
            
        else:
            orm_query = self.session.query(
                CarSalesData.car_make,
                func.avg(CarSalesData.sale_price).label('avg_price'),
                func.sum(CarSalesData.commission_earned).label('total_commission'),
                func.avg(CarSalesData.commission_rate).label('avg_commission_rate')
            ).group_by(CarSalesData.car_make).order_by(
                func.sum(CarSalesData.commission_earned).desc()
            )
            
            explanation = "Commission analysis by car brand"
        
        return {
            'orm_query': orm_query,
            'orm_description': f"Commission query using commission columns",
            'explanation': explanation,
            'error': None
        }

    def _handle_year_query_sqlalchemy(self, query):
        """Handle car year queries"""
        years = re.findall(r'\b(19|20)\d{2}\b', query)
        
        if years:
            year = int(years[0])
            if 'newer than' in query or 'after' in query:
                orm_query = self.session.query(CarSalesData).filter(
                    CarSalesData.car_year > year
                ).order_by(CarSalesData.car_year.desc()).limit(50)
                explanation = f"Cars newer than {year}"
                
            elif 'older than' in query or 'before' in query:
                orm_query = self.session.query(CarSalesData).filter(
                    CarSalesData.car_year < year
                ).order_by(CarSalesData.car_year).limit(50)
                explanation = f"Cars older than {year}"
                
            else:
                orm_query = self.session.query(CarSalesData).filter(
                    CarSalesData.car_year == year
                ).limit(50)
                explanation = f"Cars from {year}"
        else:
            # Show year distribution - FIXED: No id column
            orm_query = self.session.query(
                CarSalesData.car_year,
                func.count().label('count')  # No id reference
            ).group_by(CarSalesData.car_year).order_by(CarSalesData.car_year.desc())
            explanation = "Car count by year"
        
        return {
            'orm_query': orm_query,
            'orm_description': f"Car year query using car_year column",
            'explanation': explanation,
            'error': None
        }

    def _handle_salesperson_query_sqlalchemy(self, query):
        """Handle salesperson queries"""
        words = query.split()
        potential_names = [word for word in words if word[0].isupper() and len(word) > 2]
        
        if potential_names:
            name_pattern = ' '.join(potential_names)
            orm_query = self.session.query(CarSalesData).filter(
                CarSalesData.salesperson.ilike(f'%{name_pattern}%')
            ).limit(50)
            explanation = f"Sales by {name_pattern}"
        else:
            # Show top salespersons - FIXED: No id column
            orm_query = self.session.query(
                CarSalesData.salesperson,
                func.count().label('total_sales'),  # No id reference
                func.sum(CarSalesData.sale_price).label('total_revenue'),
                func.sum(CarSalesData.commission_earned).label('total_commission')
            ).group_by(CarSalesData.salesperson).order_by(
                func.sum(CarSalesData.commission_earned).desc()
            )
            explanation = "Salesperson performance summary"
        
        return {
            'orm_query': orm_query,
            'orm_description': f"Salesperson query",
            'explanation': explanation,
            'error': None
        }

    # =============================================================================
    # FIXED EXECUTION METHOD - NO ID COLUMN
    # =============================================================================

    def _execute_sqlalchemy_query(self, query_info):
        """FIXED execution method - no id column"""
        try:
            orm_query = query_info['orm_query']
            results = orm_query.all()
            
            if results:
                if hasattr(results[0], '__dict__'):
                    # ORM objects - convert using actual column names (NO ID)
                    return [
                        {
                            # ❌ NO id field since it doesn't exist
                            'date': r.date.isoformat() if r.date else None,
                            'salesperson': r.salesperson,
                            'customer_name': r.customer_name,
                            'car_make': r.car_make,
                            'car_model': r.car_model,
                            'car_year': r.car_year,
                            'sale_price': float(r.sale_price) if r.sale_price else None,
                            'commission_rate': float(r.commission_rate) if r.commission_rate else None,
                            'commission_earned': float(r.commission_earned) if r.commission_earned else None
                        }
                        for r in results
                    ]
                else:
                    # Aggregation results
                    if len(results) == 1 and not hasattr(results[0], '_fields'):
                        return [{'result': results[0]}]
                    else:
                        # Handle named tuple results from aggregation
                        if hasattr(results[0], '_fields'):
                            return [
                                {field: getattr(row, field) for field in row._fields}
                                for row in results
                            ]
                        else:
                            return [
                                {f'column_{i}': val for i, val in enumerate(row) if hasattr(row, '__iter__')}
                                if hasattr(results[0], '__iter__') 
                                else {'result': row}
                                for row in results
                            ]
            else:
                return []
                
        except Exception as e:
            return {'error': f"SQLAlchemy query execution failed: {str(e)}"}

    # Pattern detection methods
    def _is_count_query(self, query):
        return any(phrase in query for phrase in ['how many', 'count', 'number of'])

    def _is_time_query(self, query):
        time_phrases = ['last month', 'this month', 'last year', 'during', 'monthly', 'yearly']
        return any(phrase in query for phrase in time_phrases)

    def _is_brand_model_query(self, query):
        return any(brand in query for brand in self.car_brands) or \
               any(model in query for model in self.car_models)

    def _is_price_query(self, query):
        return any(word in query for word in ['price', 'under', 'over', 'between', 'cheap', 'expensive'])

    def _is_commission_query(self, query):
        return any(word in query for word in ['commission', 'profit', 'higher', 'highest', 'profitable'])

    def _is_year_query(self, query):
        return any(word in query for word in ['year', 'newer', 'older', 'from']) or \
               bool(re.search(r'\b(19|20)\d{2}\b', query))

    def _is_salesperson_query(self, query):
        return any(word in query for word in ['salesperson', 'sold by', 'sales by']) or \
               any(word in query for word in ['mary', 'jason', 'john', 'smith', 'lawrence'])

    def _route_query(self, user_input):
        """
        Enhanced routing: Decide whether to use PostgreSQL or BigQuery
        Routes complex multi-column queries to BigQuery for faster analytics
        """
        user_lower = user_input.lower()
        
        # Count keyword matches for each database
        bq_score = sum(1 for keyword in self.bigquery_keywords if keyword in user_lower)
        pg_score = sum(1 for keyword in self.postgresql_keywords if keyword in user_lower)
        
        print(bq_score, pg_score)
        # ==========================================================================
        # NEW: Complex Multi-Column Query Detection
        # ==========================================================================
        
        # Check if query involves multiple columns/dimensions
        complexity_score = self._calculate_query_complexity(user_lower)
        
        # If query is complex (involves multiple columns), route to BigQuery
        if complexity_score >= 2:
            print(f"🔍 Complex query detected (complexity score: {complexity_score}) - routing to BigQuery")
            return "BIGQUERY"
        
        # ==========================================================================
        # Enhanced Pattern Detection
        # ==========================================================================
        
        # Pattern 1: Multi-dimensional analytics queries -> BigQuery
        multi_column_patterns = [
            # Salesperson + performance metrics
            ['salesperson', 'highest', 'count'],
            ['salesperson', 'top', 'sales'],
            ['salesperson', 'best', 'performance'],
            ['salesperson', 'most', 'commission'],
            
            # Brand/model + analytics
            ['brand', 'highest', 'sales'],
            ['model', 'top', 'selling'],
            ['car', 'best', 'performance'],
            
            # Time + multiple dimensions
            ['month', 'salesperson', 'performance'],
            ['year', 'brand', 'sales'],
            ['monthly', 'commission', 'analysis'],
            
            # Commission + other dimensions
            ['commission', 'salesperson', 'comparison'],
            ['profit', 'model', 'analysis'],
            ['revenue', 'brand', 'breakdown'],
            
            # Complex aggregations
            ['average', 'by', 'salesperson'],
            ['total', 'per', 'brand'],
            ['sum', 'group', 'by'],
            ['rank', 'by', 'performance']
        ]
        
        # Check if query matches multi-column patterns
        for pattern in multi_column_patterns:
            if all(word in user_lower for word in pattern):
                print(f"🎯 Multi-column pattern detected: {pattern} - routing to BigQuery")
                return "BIGQUERY"
        
        # ==========================================================================
        # Existing Routing Logic (Enhanced)
        # ==========================================================================
        
        # Pattern 2: Count queries with analytics -> BigQuery, simple counts -> PostgreSQL
        if any(word in user_lower for word in ['how many', 'count', 'total']):
            # Complex count queries with grouping/analytics
            if any(word in user_lower for word in ['by salesperson', 'by brand', 'by model', 'by year', 
                                                  'per salesperson', 'per brand', 'per model',
                                                  'group by', 'grouped by', 'breakdown']):
                return "BIGQUERY"
            # Time-based counts
            elif any(word in user_lower for word in ['last month', 'monthly', 'trend', 'analysis']):
                return "BIGQUERY"
            # Simple direct counts
            else:
                return "POSTGRESQL"
        
        # Pattern 3: Aggregation and ranking queries -> BigQuery
        if any(word in user_lower for word in ['average', 'highest', 'lowest', 'commission', 
                                              'sum', 'total', 'rank', 'ranking', 'top', 'best',
                                              'performance', 'comparison', 'analysis']):
            return "BIGQUERY"
        
        # Pattern 4: Simple lookups -> PostgreSQL
        if any(word in user_lower for word in ['find customer', 'show record', 'specific',
                                              'find', 'show me', 'get', 'lookup']):
            # But if it involves analytics, send to BigQuery
            if any(word in user_lower for word in ['performance', 'sales', 'commission', 'ranking']):
                return "BIGQUERY"
            else:
                return "POSTGRESQL"
        
        # Pattern 5: Time-based queries -> mostly BigQuery for analytics
        if any(word in user_lower for word in ['last month', 'this month', 'last year', 'monthly', 
                                              'yearly', 'quarterly', 'trend']):
            return "BIGQUERY"
        
        # ==========================================================================
        # Final Decision Based on Scores
        # ==========================================================================
        
        # If BigQuery score significantly higher, use BigQuery
        if bq_score > pg_score + 1:  # Need clear preference for BigQuery
            return "BIGQUERY"
        # For ties or slight PostgreSQL preference, check complexity
        elif bq_score == pg_score and complexity_score >= 1:
            return "BIGQUERY"
        else:
            return "POSTGRESQL"

    def _calculate_query_complexity(self, user_lower):
        """
        Calculate query complexity based on number of dimensions/columns involved
        Higher score = more complex = better suited for BigQuery analytics
        """
        complexity_score = 0
        
        # Column references (each adds to complexity)
        column_references = {
            'salesperson': ['salesperson', 'sales person', 'seller', 'agent'],
            'customer': ['customer', 'client', 'buyer'],
            'car_make': ['brand', 'make', 'manufacturer'],
            'car_model': ['model', 'car model', 'vehicle'],
            'car_year': ['year', 'model year'],
            'price': ['price', 'cost', 'amount', 'value'],
            'commission': ['commission', 'profit', 'earning'],
            'date': ['date', 'time', 'when', 'month', 'year']
        }
        
        # Count how many different column types are referenced
        columns_mentioned = 0
        for column_type, keywords in column_references.items():
            if any(keyword in user_lower for keyword in keywords):
                columns_mentioned += 1
        
        complexity_score += columns_mentioned
        
        # Analytical operations (each adds complexity)
        analytical_operations = [
            'highest', 'lowest', 'best', 'worst', 'top', 'bottom',
            'average', 'avg', 'sum', 'total', 'count',
            'rank', 'ranking', 'compare', 'comparison',
            'analysis', 'breakdown', 'performance',
            'group by', 'grouped by', 'per', 'by'
        ]
        
        analytical_ops_count = sum(1 for op in analytical_operations if op in user_lower)
        complexity_score += analytical_ops_count
        
        # Superlative/comparative words indicate complex analysis
        superlatives = ['most', 'least', 'better', 'worse', 'greater', 'lesser']
        if any(word in user_lower for word in superlatives):
            complexity_score += 1
        
        # Multiple entities in same query
        if user_lower.count(' and ') >= 1 or user_lower.count(' with ') >= 1:
            complexity_score += 1
        
        # Question words that often lead to complex queries
        complex_question_words = ['which', 'what', 'who', 'where', 'how']
        if any(word in user_lower for word in complex_question_words):
            complexity_score += 0.5
        
        return complexity_score

    # =============================================================================
    # BIGQUERY SQL GENERATION - REAL IMPLEMENTATION
    # =============================================================================
    
    def _convert_to_sql(self, user_input, database):
        """Convert natural language to BigQuery SQL"""
        user_lower = user_input.lower()
        print(user_lower)
        try:
            print("🔍 Generating SQL with SimpleSQLGeneratorQ...")
            result = self.simple_sql_generatorq.generate_sql(user_lower)
            print(result, " < - - -  -  - - - -")
            # # Complex multi-column queries for BigQuery
            # if self._is_complex_analytics_query(user_lower):
            #     return self._handle_complex_analytics_query(user_lower)
            # elif self._is_count_query(user_lower):
            #     return self._handle_count_query_bigquery(user_lower)
            # elif self._is_time_query(user_lower):
            #     return self._handle_time_query_bigquery(user_lower)
            # elif self._is_commission_query(user_lower):
            #     return self._handle_commission_query_bigquery(user_lower)
            # else:
            # FIX: Check if result is dict and extract SQL
            if isinstance(result, dict):
                if result.get('error'):
                    return {
                        'sql': None,
                        'explanation': None,
                        'error': result['error']
                    }
                else:
                    return {
                        'sql': result.get('sql'),  # Extract the SQL string
                        'explanation': result.get('explanation', 'Generated SQL query'),
                        'error': None
                    }
            else:
                # If it's just a string (unlikely)
                return {
                    'sql': result,
                    'explanation': 'Generated SQL query',
                    'error': None
                }
            # return {
            #         'sql': result,
            #         'explanation': None,
            #     }
                
        except Exception as e:
            return {
                'sql': None,
                'explanation': None,
                'error': f"Error generating BigQuery SQL: {str(e)}"
            }

    def _is_complex_analytics_query(self, query):
        """Detect complex analytics queries that need special handling"""
        complex_patterns = [
            ['salesperson', 'highest', 'count'],
            ['salesperson', 'most', 'sales'],
            ['top', 'salesperson'],
            ['best', 'performance'],
            ['which', 'salesperson'],
            ['who', 'sold', 'most']
        ]
        
        return any(all(word in query for word in pattern) for pattern in complex_patterns)

    def _handle_complex_analytics_query(self, query):
        """Handle complex multi-dimensional analytics queries"""
        
        # Pattern: "salesperson with highest sale count and which model car was it"
        if all(word in query for word in ['salesperson', 'highest', 'count']) or \
           all(word in query for word in ['salesperson', 'most', 'sales']):
            
            sql = f"""
                WITH salesperson_stats AS (
                    SELECT 
                        salesperson,
                        COUNT(*) as sale_count,
                        SUM(sale_price) as total_revenue,
                        SUM(commission_earned) as total_commission
                    FROM {self.bq_table_ref}
                    GROUP BY salesperson
                    ORDER BY sale_count DESC
                    LIMIT 1
                ),
                top_salesperson_details AS (
                    SELECT 
                        s.salesperson,
                        s.sale_count,
                        s.total_revenue,
                        s.total_commission,
                        cs.car_make,
                        cs.car_model,
                        COUNT(*) as model_count
                    FROM salesperson_stats s
                    JOIN {self.bq_table_ref} cs ON s.salesperson = cs.salesperson
                    GROUP BY s.salesperson, s.sale_count, s.total_revenue, s.total_commission, cs.car_make, cs.car_model
                    ORDER BY model_count DESC
                    LIMIT 5
                )
                SELECT 
                    salesperson,
                    sale_count,
                    total_revenue,
                    total_commission,
                    car_make,
                    car_model,
                    model_count as times_sold_this_model
                FROM top_salesperson_details
                ORDER BY model_count DESC
            """
            
            explanation = "Finding salesperson with highest sale count and their most sold car models"
            
        # Pattern: "which salesperson sold the most expensive cars"
        elif all(word in query for word in ['salesperson', 'most', 'expensive']):
            
            sql = f"""
                SELECT 
                    salesperson,
                    COUNT(*) as total_sales,
                    AVG(sale_price) as avg_sale_price,
                    MAX(sale_price) as highest_sale_price,
                    SUM(sale_price) as total_revenue,
                    car_make,
                    car_model
                FROM {self.bq_table_ref}
                WHERE sale_price > (
                    SELECT PERCENTILE_CONT(sale_price, 0.8) OVER() as expensive_threshold
                    FROM {self.bq_table_ref}
                    LIMIT 1
                )
                GROUP BY salesperson, car_make, car_model
                ORDER BY avg_sale_price DESC, total_sales DESC
                LIMIT 10
            """
            
            explanation = "Finding salespersons who sold the most expensive cars"
            
        # Pattern: "top performing salesperson by commission"
        elif all(word in query for word in ['top', 'salesperson', 'commission']):
            
            sql = f"""
                SELECT 
                    salesperson,
                    COUNT(*) as total_sales,
                    SUM(sale_price) as total_revenue,
                    SUM(commission_earned) as total_commission,
                    AVG(commission_rate) as avg_commission_rate,
                    AVG(sale_price) as avg_sale_price,
                    STRING_AGG(DISTINCT car_make, ', ') as brands_sold
                FROM {self.bq_table_ref}
                GROUP BY salesperson
                ORDER BY total_commission DESC
                LIMIT 10
            """
            
            explanation = "Top performing salespersons ranked by total commission earned"
            
        else:
            # Generic complex query
            sql = f"""
                SELECT 
                    salesperson,
                    COUNT(*) as sale_count,
                    SUM(sale_price) as total_revenue,
                    AVG(sale_price) as avg_price,
                    SUM(commission_earned) as total_commission,
                    car_make,
                    car_model,
                    COUNT(*) as model_sales
                FROM {self.bq_table_ref}
                GROUP BY salesperson, car_make, car_model
                ORDER BY sale_count DESC, total_commission DESC
                LIMIT 20
            """
            
            explanation = "Complex analytics query - salesperson performance with car model breakdown"
        
        return {
            'sql': sql,
            'explanation': explanation,
            'error': None
        }

    def _handle_count_query_bigquery(self, query):
        """Handle count queries for BigQuery"""
        model_found = None
        brand_found = None
        
        for model in self.car_models:
            if model in query:
                model_found = model
                break
        
        for brand in self.car_brands:
            if brand in query:
                brand_found = brand
                break
        
        if model_found:
            sql = f"""
                SELECT COUNT(*) as total_count
                FROM {self.bq_table_ref}
                WHERE LOWER(car_model) LIKE '%{model_found}%'
            """
            explanation = f"Counting all {model_found} cars in BigQuery"
            
        elif brand_found:
            sql = f"""
                SELECT COUNT(*) as total_count
                FROM {self.bq_table_ref}
                WHERE LOWER(car_make) = '{brand_found}'
            """
            explanation = f"Counting all {brand_found} cars in BigQuery"
            
        else:
            sql = f"SELECT COUNT(*) as total_count FROM {self.bq_table_ref}"
            explanation = "Counting all cars in BigQuery"
        
        return {'sql': sql, 'explanation': explanation, 'error': None}

    def _handle_time_query_bigquery(self, query):
        """Handle time-based queries for BigQuery"""
        if 'last month' in query:
            sql = f"""
                SELECT 
                    COUNT(*) as total_sales,
                    SUM(sale_price) as total_revenue,
                    AVG(sale_price) as avg_price,
                    SUM(commission_earned) as total_commission
                FROM {self.bq_table_ref}
                WHERE date >= DATE_SUB(DATE_TRUNC(CURRENT_DATE(), MONTH), INTERVAL 1 MONTH)
                AND date < DATE_TRUNC(CURRENT_DATE(), MONTH)
            """
            explanation = "Sales data for last month using BigQuery"
            
        elif 'this month' in query:
            sql = f"""
                SELECT 
                    COUNT(*) as total_sales,
                    SUM(sale_price) as total_revenue,
                    AVG(sale_price) as avg_price,
                    SUM(commission_earned) as total_commission
                FROM {self.bq_table_ref}
                WHERE date >= DATE_TRUNC(CURRENT_DATE(), MONTH)
            """
            explanation = "Sales data for this month using BigQuery"
        
        return {'sql': sql, 'explanation': explanation, 'error': None}

    def _handle_commission_query_bigquery(self, query):
        """Handle commission queries for BigQuery"""
        if 'highest' in query or 'higher' in query:
            sql = f"""
                SELECT 
                    salesperson,
                    car_make,
                    car_model,
                    sale_price,
                    commission_rate,
                    commission_earned,
                    date
                FROM {self.bq_table_ref}
                WHERE commission_earned > (
                    SELECT AVG(commission_earned) FROM {self.bq_table_ref}
                )
                ORDER BY commission_earned DESC
                LIMIT 20
            """
            explanation = "Cars with above-average commission using BigQuery"
            
        else:
            sql = f"""
                SELECT 
                    car_make,
                    COUNT(*) as total_sales,
                    AVG(sale_price) as avg_price,
                    SUM(commission_earned) as total_commission,
                    AVG(commission_rate) as avg_commission_rate
                FROM {self.bq_table_ref}
                GROUP BY car_make
                ORDER BY total_commission DESC
            """
            explanation = "Commission analysis by car brand using BigQuery"
        
        return {'sql': sql, 'explanation': explanation, 'error': None}

    def _execute_query(self, sql, database):
        """Execute BigQuery SQL queries"""
        try:
            print("🚀 Executing SQL on calvin", database)
            print(f"SQL query: {sql}")
            if database == "BIGQUERY":
                results = self.bq_client.query(sql)
                return [dict(row.items()) for row in results]
            else:
                # Fallback for other databases
                return [{'result': f'Database {database} not implemented'}]
                
        except Exception as e:
            return {'error': f"BigQuery execution failed: {str(e)}"}


    def __del__(self):
        if hasattr(self, 'session') and self.session:
            self.session.close()

# Usage
def main():

    global simple_gen

    simple_gen =  SimpleSQLGenerator(
        api_key=""
    )


    psql_config = {
        'host': 'localhost',
        'database': 'car_sales_data',
        'user': 'david',
        'password': 'david'
    }
    
    BIGQUERY_CREDENTIALS = "/home/ubuntu/Rag-Assignment/bqKeys.json"
    PROJECT_ID = "primeval-array-469815-c9"
    DATASET_ID = "car_sales_dataset"
    TABLE_ID = "car_sales_data"
    
    try:
        query_system = SmartQuerySystemWithSQLAlchemy(
            psql_config=psql_config,
            bigquery_credentials_path=BIGQUERY_CREDENTIALS,
            project_id=PROJECT_ID,
            dataset_id=DATASET_ID,
            table_id=TABLE_ID,
            simple_generator=simple_gen,
        )
        
        query_system.get_table_schema()
        query_system.test_connections()
        
        test_queries = [
            "salesperson with highest sale count and which model car model was it",
            # "how many cars are corolla",
            # "show me ford cars",
            # "cars from 2018",
            # "sales by Mary Lawrence"
        ]
        
        print("\n🚀 Testing FIXED Smart Query System")
        print("=" * 60)
        
        for query in test_queries:
            print(f"\n📝 Query: '{query}'")
            result = query_system.process_user_query(query)
            
            if 'error' not in result:
                print(f"🎯 Routed to: {result['routed_to']}")
                print(f"🔧 Generated Query: {result['generated_query']}")
                print(f"💡 Explanation: {result['explanation']}")
                print(f"📊 Results count: {len(result['results']) if isinstance(result['results'], list) else 'Error'}")
                
                # Show first few results if available
                if isinstance(result['results'], list) and result['results']:
                    print(f"📄 Sample results:")
                    for i, record in enumerate(result['results'][:2]):  # Show first 2
                        print(f"   {i+1}. {record}")
            else:
                print(f"❌ Error: {result['error']}")
            
            print("-" * 40)
            
    except Exception as e:
        print(f"❌ System initialization failed: {e}")

if __name__ == "__main__":
    main()
