import textwrap
from agents import Agent, function_tool
from settings import OPENAI_NON_REASONING_MODEL_NAME

# Internal LLM agent for contract generation
contract_generator = Agent(
    name="Nagini Contract Generator",
    instructions="""You are an expert in formal verification and Nagini contracts. 
    Convert natural language specifications to formal Python contracts using Nagini syntax.
    
    Use these Nagini constructs:
    - Preconditions: Requires(condition)
    - Postconditions: Ensures(condition) 
    - Invariants: Invariant(condition)
    - Assertions: Assert(condition)
    - Pure functions: @Pure
    - Ghost variables for specification
    
    Always provide complete, syntactically correct Nagini contracts.""",
    model=OPENAI_NON_REASONING_MODEL_NAME,
)

test_case_generator = Agent(
    name="Test Case Generator",
    instructions="""You are an expert test engineer. Generate comprehensive test cases in pytest format.
    
    Include:
    - Happy path tests
    - Boundary value tests
    - Error condition tests
    - Edge cases
    - Property-based tests where appropriate
    
    Generate actual executable Python test code using pytest and hypothesis when appropriate.""",
    model=OPENAI_NON_REASONING_MODEL_NAME,
)

edge_case_analyzer = Agent(
    name="Edge Case Analyzer",
    instructions="""You are an expert at identifying edge cases and corner conditions.
    
    Analyze specifications for:
    - Boundary conditions
    - Empty/null inputs
    - Maximum/minimum values
    - Concurrent access issues
    - Resource exhaustion
    - Invalid state transitions
    - Error propagation scenarios
    
    Provide specific, actionable edge cases with clear descriptions.""",
    model=OPENAI_NON_REASONING_MODEL_NAME,
)

@function_tool
def generate_contract(natural_language_spec: str) -> str:
    """Converts natural language to formal Python contracts (Nagini)."""
    try:
        prompt = f"""
        Convert this natural language specification to Nagini contracts:
        
        Specification: {natural_language_spec}
        
        Provide:
        1. Function signature with type hints
        2. Preconditions using Requires()
        3. Postconditions using Ensures()
        4. Any necessary invariants
        5. Complete example with imports
        
        Example format:
        ```python
        from nagini_contracts.contracts import *
        
        def function_name(param: type) -> return_type:
            Requires(precondition)
            Ensures(postcondition)
            # implementation
        ```
        """
        
        from agents import Runner
        runner = Runner(contract_generator)
        result = runner.run(prompt)
        
        return f"Generated Nagini Contract:\n{result.messages[-1].content}"
        
    except Exception as e:
        return f"Error generating contract: {str(e)}\nFallback basic contract structure provided."

@function_tool
def generate_test_cases(natural_language_spec: str, contract_code: str = "") -> str:
    """Generates comprehensive test cases from specification."""
    try:
        prompt = f"""
        Generate comprehensive pytest test cases for this specification:
        
        Specification: {natural_language_spec}
        
        {f"Contract Code: {contract_code}" if contract_code else ""}
        
        Generate:
        1. Test class with descriptive name
        2. Setup/teardown methods if needed
        3. Happy path tests
        4. Boundary condition tests
        5. Error condition tests
        6. Property-based tests using hypothesis if applicable
        
        Use pytest conventions and include assertions that verify the contract conditions.
        """
        
        from agents import Runner
        runner = Runner(test_case_generator)
        result = runner.run(prompt)
        
        return f"Generated Test Cases:\n{result.messages[-1].content}"
        
    except Exception as e:
        return f"Error generating test cases: {str(e)}\nBasic test structure recommended."

@function_tool
def identify_edge_cases(natural_language_spec: str) -> str:
    """Identifies edge cases in the specification."""
    try:
        prompt = f"""
        Analyze this specification and identify potential edge cases:
        
        Specification: {natural_language_spec}
        
        Consider:
        1. Input boundary conditions
        2. Resource limitations
        3. Concurrent access scenarios
        4. Error propagation
        5. State transition edge cases
        6. Performance edge cases
        7. Security considerations
        
        Provide specific scenarios with clear descriptions of what could go wrong.
        """
        
        from agents import Runner
        runner = Runner(edge_case_analyzer)
        result = runner.run(prompt)
        
        return f"Identified Edge Cases:\n{result.messages[-1].content}"
        
    except Exception as e:
        return f"Error identifying edge cases: {str(e)}\nManual analysis recommended."

@function_tool
def validate_nagini_syntax(contract_code: str) -> str:
    """Validates Nagini contract syntax."""
    try:
        # Basic syntax validation
        required_imports = ["from nagini_contracts.contracts import"]
        nagini_keywords = ["Requires", "Ensures", "Invariant", "Assert", "Pure"]
        
        issues = []
        
        # Check for required imports
        if not any(imp in contract_code for imp in required_imports):
            issues.append("Missing Nagini contracts import")
        
        # Check for proper contract usage
        if "Requires(" not in contract_code and "Ensures(" not in contract_code:
            issues.append("No preconditions or postconditions found")
        
        # Basic Python syntax check
        try:
            compile(contract_code, '<string>', 'exec')
        except SyntaxError as e:
            issues.append(f"Python syntax error: {e}")
        
        if issues:
            return f"Validation Issues Found:\n" + "\n".join(f"- {issue}" for issue in issues)
        else:
            return "✓ Nagini contract syntax appears valid"
            
    except Exception as e:
        return f"Error during validation: {str(e)}"

specification_agent = Agent(
    name="Specification Agent",
    instructions="""
    You are a formal verification expert specializing in Nagini contracts.
    
    Your capabilities:
    1. Convert natural language to formal Nagini contracts
    2. Generate comprehensive test cases
    3. Identify edge cases and corner conditions
    4. Validate contract syntax
    
    When users provide specifications:
    1. Ask clarifying questions if the specification is ambiguous
    2. Generate formal contracts with proper preconditions and postconditions
    3. Create corresponding test cases
    4. Identify potential edge cases
    5. Validate the generated contracts
    
    Always explain your reasoning and provide actionable output.
    """,
    tools=[generate_contract, generate_test_cases, identify_edge_cases, validate_nagini_syntax],
)
