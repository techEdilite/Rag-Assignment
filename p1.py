import streamlit as st
from sqlAlchemy import SmartQuerySystemWithSQLAlchemy
from bigQueryhandler import SimpleSQLGenerator
import re
import rag

def classify_query_rule_based(query: str):
    """
    Classify a query into structured, unstructured, or mixed based on keyword matching.
    Also return parts of the sentence that match each type.
    """
    # Define keyword lists (expand as needed)
    structured_keywords = [
        "count", "number", "how many", "total", "sum", "average", "list", "top", "greater than", "less than", 
        "statistics", "amount", "percentage", "data"
    ]
    unstructured_keywords = [
        "explain", "describe", "reason", "why", "meaning", "details", "summary", "information", "policy", "content"
    ]

    # Normalize query to lowercase
    q_lower = query.lower()

    # Split into words for scanning (simple, could improve using NLP)
    words = re.findall(r'\w+', q_lower)

    structured_hits = []
    unstructured_hits = []

    # Check each word or phrase
    for word in words:
        if word in [kw for kw in structured_keywords if " " not in kw]:
            structured_hits.append(word)
        if word in [kw for kw in unstructured_keywords if " " not in kw]:
            unstructured_hits.append(word)
    
    # Check multi-word phrases (like "how many", "greater than")
    for phrase in structured_keywords:
        if " " in phrase and phrase in q_lower:
            structured_hits.append(phrase)
    for phrase in unstructured_keywords:
        if " " in phrase and phrase in q_lower:
            unstructured_hits.append(phrase)

    # Decide classification
    total_hits = len(structured_hits) + len(unstructured_hits)
    if total_hits == 0:
        classification = "unknown"
        structured_pct = 0
        unstructured_pct = 0
    else:
        structured_pct = (len(structured_hits) / total_hits) * 100
        unstructured_pct = (len(unstructured_hits) / total_hits) * 100

        if structured_pct > 70:
            classification = "structured"
        elif unstructured_pct > 70:
            classification = "unstructured"
        else:
            classification = "mixed"

    # For mixed queries, attempt to split
    structured_part = []
    unstructured_part = []
    if classification == "mixed":
        for token in re.split(r'(\.|\?|\!|\,|and|or)', query):
            token_l = token.lower()
            if any(kw in token_l for kw in structured_keywords):
                structured_part.append(token.strip())
            elif any(kw in token_l for kw in unstructured_keywords):
                unstructured_part.append(token.strip())

    return {
        "classification": classification,
        "structured_hits": structured_hits,
        "unstructured_hits": unstructured_hits,
        "structured_pct": structured_pct,
        "unstructured_pct": unstructured_pct,
        "structured_segments": structured_part,
        "unstructured_segments": unstructured_part
    }


# Initialize system components at module level to avoid recreation
@st.cache_resource
def initialize_system():
    """Initialize the query system once and cache it"""
    try:
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


        # Initialize query system with the generator
        query_system = SmartQuerySystemWithSQLAlchemy(
            psql_config=psql_config,
            bigquery_credentials_path=BIGQUERY_CREDENTIALS,
            project_id=PROJECT_ID,
            dataset_id=DATASET_ID,
            table_id=TABLE_ID,
)
        
        return query_system
        
    except Exception as e:
        st.error(f"Failed to initialize system: {str(e)}")
        return None

def is_smalltalk(prompt: str) -> bool:
    # Define phrases that clearly indicate small talk
    smalltalk_phrases = [
        "hi",
        "hello",
        "hey",
        "good morning",
        "good evening",
        "how are you",
        "whats is this"
        "who are you",
        "what's up",
        "how's it going"
    ]
    
    prompt_clean = re.sub(r'[^a-zA-Z0-9\s]', '', prompt.lower().strip())  # remove punctuation
    
    for phrase in smalltalk_phrases:
        if phrase in prompt_clean:
            return True
    return False

def process_user_input(user_prompt, query_system):
    """
    Process user input using the query system
    """
    if query_system is None:
        return "System initialization failed. Please check configuration."
    
    try:
        if is_smalltalk(user_prompt):  # or classify_intent(user_prompt) == "smalltalk"
           return {
            "user_query": user_prompt,
            "routed_to": "SMALLTALK",
            "response": "Hello! How can I assist you with car data or reports today?"
           }
    
        result = query_system.process_user_query(user_prompt)
        print(rag.search_and_answer(user_prompt), " < - - -")
        # result.content: rag.search_and_answer(user_prompt)
        result["rag_content"] = rag.search_and_answer(user_prompt)["answer"]

        return result
    except Exception as e:
        return f"Error processing query: {str(e)}"


def main():
    st.title("Hybrid Query System")
    st.write("Enter your question to query both structured and unstructured data")
    
    # Initialize system
    query_system = initialize_system()

    documents_folder = "./"  # Change this to your folder path
    
    print("🚀 Document Processing and Search System")
    print("=" * 50)
    rag.embed_and_store_documents(documents_folder)
    if query_system is None:
        st.error("System failed to initialize. Please check your configuration.")
        return
    
    # Get user input
    user_input = st.text_area(
        "Your question:", 
        placeholder="Type your question here...",
        help="Examples: 'Show me total sales by brand', 'Explain the sales trends', 'Count of Toyota cars sold'"
    )
    
    # Add some example buttons
    st.subheader("Example Queries")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Total Sales by Brand"):
            st.session_state.example_query = "Show me total sales by brand"
    
    with col2:
        if st.button("Count Toyota Cars"):
            st.session_state.example_query = "How many Toyota cars were sold?"
    
    with col3:
        if st.button("Top Salespersons"):
            st.session_state.example_query = "Who are the top 5 salespersons by commission?"
    
    # Use example query if button was clicked
    if 'example_query' in st.session_state:
        user_input = st.session_state.example_query
        del st.session_state.example_query
    
    # Process button
    if st.button("Process Query", type="primary"):
        if user_input.strip():
            with st.spinner("Processing your query..."):
                # Call the processing function
                result = process_user_input(user_input, query_system)
                
                # Display result
                st.success("Processing complete!")
                st.subheader("Query Analysis")
                
                # Show classification
                classification = classify_query_rule_based(user_input)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Query Type", classification["classification"].title())
                with col2:
                    if classification["classification"] != "unknown":
                        structured_pct = classification["structured_pct"]
                        st.metric("Structured %", f"{structured_pct:.0f}%")
                
                # Show hits
                if classification["structured_hits"]:
                    st.write("**Structured Keywords Found:**", ", ".join(classification["structured_hits"]))
                if classification["unstructured_hits"]:
                    st.write("**Unstructured Keywords Found:**", ", ".join(classification["unstructured_hits"]))
                
                st.subheader("Result")
                st.write(result)
        else:
            st.warning("Please enter a question first.")
    
    # Add system status in sidebar
    with st.sidebar:
        st.subheader("System Status")
        if query_system:
            st.success("✅ System Initialized")
            try:
                # You can add connection tests here if your SmartQuerySystemWithSQLAlchemy has test methods
                # query_system.test_connections()
                st.success("✅ Database Connections Ready")
            except:
                st.warning("⚠️ Database Connection Issues")
        else:
            st.error("❌ System Not Initialized")
        
        st.subheader("Configuration")
        st.write("**PostgreSQL**: localhost/car_sales_data")
        st.write("**BigQuery**: primeval-array-469815-c9")
        st.write("**LLM**: Groq/Llama3-8B")


if __name__ == "__main__":
    main()
