from .output_parser import OutputParser

class QueryOutputParser(OutputParser):
    """
    The Output Parser for search queries
    """
    def parse(self, output:str) -> str:
        """Fix the given query"""
        output = output.strip("\\")
        return output.replace("\"", "").strip()