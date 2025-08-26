import re
from typing import Dict
from groq import Groq

class SimpleSQLGenerator:
    def __init__(self, groq_api_key: str, table_name: str = "car_sales"):
        self.client = Groq(api_key=groq_api_key)
        self.table_name = table_name
        
        # Simple column information
        self.columns_info = """
Available columns in {table_name}:
- salesperson (string): Name of the sales person
- customer (string): Customer name  
- car_make (string): Car brand (Toyota, Honda, BMW, Mercedes, Ford)
- car_model (string): Car model name
- car_year (integer): Manufacturing year
- sale_price (decimal): Final sale price
- commission_rate (decimal): Commission percentage
- commission_earned (decimal): Commission amount
- sale_date (date): Date of sale
- customer_age (integer): Customer age
- financing (boolean): Whether financing was used

Common synonyms:
- "brand" = car_make
- "price" = sale_price  
- "commission" = commission_earned
- "seller/agent" = salesperson
- "buyer" = customer
        """.format(table_name=table_name)

    def generate_sql(self, user_query: str, database_type: str = "bigquery") -> Dict:
        """Generate SQL directly from user query"""
        
        prompt = f"""You are a SQL expert. Convert this natural language query to {database_type} SQL.
    
USER QUERY: "{user_query}"
TABLE: car_sales_dataset.car_sales_data, this how table should be used, not just car_sales_data, instead  car_sales_dataset.car_sales_data
{self.columns_info}

INSTRUCTIONS:
1. Generate ONLY valid {database_type} SQL
2. Use proper {database_type} syntax 
3. Handle aggregations (COUNT, SUM, AVG, MAX, MIN) properly
4. Use appropriate WHERE, GROUP BY, HAVING, ORDER BY clauses
5. Add LIMIT when reasonable
6. For BigQuery, use DATE functions like CURRENT_DATE()
7. For PostgreSQL, use NOW(), CURRENT_DATE
8.Always generate single query not individual queries

EXAMPLES:
- "Show all Toyota sales" → SELECT * FROM car_sales_dataset.car_sales_data WHERE car_make = 'Toyota' LIMIT 100
- "Average price by brand" → SELECT car_make, AVG(sale_price) as avg_price FROM car_sales_dataset.car_sales_data GROUP BY car_make ORDER BY avg_price DESC
- "Salesperson with more than 10 sales" → SELECT salesperson, COUNT(*) as sales_count FROM car_sales_dataset.car_sales_data GROUP BY salesperson HAVING COUNT(*) > 10 ORDER BY sales_count DESC

Return ONLY the SQL query, no explanations or formatting:"""

        try:
            response = self.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": f"Generate only valid {database_type} SQL queries. No explanations, no markdown, just SQL."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=300
            )
            
            sql_query = response.choices[0].message.content.strip()
            
            # Clean up any markdown or extra text
            sql_query = self._clean_sql_response(sql_query)
            
            # Basic validation
            if self._is_valid_sql(sql_query):
                return {
                    'sql': sql_query,
                    'explanation': f"Generated {database_type} query for: {user_query}",
                    'error': None
                }
            else:
                return {
                    'sql': None,
                    'explanation': None,
                    'error': f"Generated invalid SQL: {sql_query}"
                }
                
        except Exception as e:
            return {
                'sql': None,
                'explanation': None,
                'error': f"Error generating SQL: {str(e)}"
            }

    def _clean_sql_response(self, response: str) -> str:
        """Clean up LLM response to extract just the SQL"""
        # Remove markdown code blocks
        if "```sql" in response:
            response = re.sub(r'```sql\s*', '', response)
            response = re.sub(r'```\s*', '', response)
        elif "```" in response:
            response = re.sub(r'```\s*', '', response)
        
        # Remove common prefixes
        response = re.sub(r'^(SQL|Query|Here\'s the SQL|The SQL is):\s*', '', response, flags=re.IGNORECASE)
        
        # Clean up whitespace
        response = response.strip()
        
        # Remove trailing semicolon if present (some systems don't like it)
        if response.endswith(';'):
            response = response[:-1]
        
        return response

    def _is_valid_sql(self, sql: str) -> bool:
        """Basic SQL validation"""
        if not sql:
            return False
        
        # Check for basic SQL structure
        sql_upper = sql.upper()
        
        # Must start with SELECT
        if not sql_upper.strip().startswith('SELECT'):
            return False
        
        # Must contain FROM with our table
        if 'FROM' not in sql_upper or self.table_name not in sql:
            return False
        
        # Check for dangerous operations (basic safety)
        dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'CREATE', 'ALTER', 'TRUNCATE']
        if any(keyword in sql_upper for keyword in dangerous_keywords):
            return False
        
        return True


# Even simpler version for complex queries
class UltraSimpleSQLGenerator:
    def __init__(self, groq_api_key: str, table_name: str = "car_sales"):
        self.client = Groq(api_key=groq_api_key)
        self.table_name = table_name

    def generate_sql(self, user_query: str, columns_list: list, database_type: str = "bigquery") -> Dict:
        """Ultra simple - just pass columns and let LLM figure it out"""
        
        columns_str = ", ".join(columns_list)
        
        prompt = f"""Convert to {database_type} SQL:

Query: "{user_query}"
Table: {self.table_name}  
Columns: {columns_str}

Return only the SQL query:"""

        try:
            response = self.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=200
            )
            
            sql = response.choices[0].message.content.strip()
            
            # Basic cleanup
            if "```" in sql:
                sql = re.sub(r'```.*?```', '', sql, flags=re.DOTALL)
                sql = sql.strip()
            
            if sql.endswith(';'):
                sql = sql[:-1]
            
            return {
                'sql': sql,
                'explanation': f"Generated SQL for: {user_query}",
                'error': None
            }
            
        except Exception as e:
            return {
                'sql': None,
                'explanation': None, 
                'error': str(e)
            }


# Test both versions
def test_generators():
    api_key = ""
    
    # Test simple version
    print("=== SIMPLE VERSION ===")
    simple_gen = SimpleSQLGenerator(api_key)
    
    queries = [
        # "",/
        # "Salesperson with more/' than 10 sales", 
        "Average price by brand and Show me all Toyota sales"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        result = simple_gen.generate_sql(query)
        print(f"SQL: {result['sql']}")
        if result['error']:
            print(f"Error: {result['error']}")
    
    # Test ultra simple version
    print(f"\n\n=== ULTRA SIMPLE VERSION ===")
    ultra_gen = UltraSimpleSQLGenerator(api_key)
    columns = ["salesperson", "customer", "car_make", "car_model", "sale_price", "commission_earned", "sale_date"]
    
    for query in queries:
        print(f"\nQuery: {query}")
        result = ultra_gen.generate_sql(query, columns)
        print(f"SQL: {result['sql']}")
        if result['error']:
            print(f"Error: {result['error']}")

if __name__ == "__main__":
    test_generators()
