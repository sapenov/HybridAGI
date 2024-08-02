import dspy
from .tool import Tool
from typing import Optional, Callable
from hybridagi.core.datatypes import (
    ToolInput,
    Query,
)
from hybridagi.core.graph_program import (
    GraphProgramList,
)
from hybridagi.output_parsers import PredictionOutputParser

class ProgramSearchSignature(dspy.Signature):
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    query = dspy.OutputField(desc = "The similarity search query")

class ProgramSearchTool(Tool):
    def __init__(
            self,
            retriever: dspy.Module,
            lm: Optional[dspy.LM] = None,
        ):
        super().__init__(name = "ProgramSearch", lm = lm)
        self.retriever = retriever
        self.predict = dspy.Predict(ProgramSearchSignature)
        self.prediction_parser = PredictionOutputParser()
        
    def program_search(self, query: str):
        retriver_input = Query(query=query)
        return self.retriever(retriver_input)
    
    def forward(self, tool_input: ToolInput) -> GraphProgramList:
        if not tool_input.disable_inference:
            with dspy.context(lm=self.lm if self.lm is not None else dspy.settings.lm):
                pred = self.predict(
                    objective = tool_input.objective,
                    context = tool_input.context,
                    purpose = tool_input.purpose,
                    prompt = tool_input.prompt,
                )
            pred.query = self.prediction_parser.parse(
                pred.query,
                prefix = "Query:",
            )
            program_list = self.program_search(pred.query)
            return program_list
        else:
            program_list = self.program_search(tool_input.prompt)
            return program_list