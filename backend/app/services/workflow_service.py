from sqlalchemy.orm import Session

from app.workflow.graph import graph

from app.core.ids import new_workflow_id

from langgraph.types import Command

class WorkflowService:

    def __init__(self, db: Session):
        self.db = db

    def start_intake(self, referral: str):

        state = {"referral": referral,}

        workflow_id = new_workflow_id()

        config = {"configurable": {"thread_id": workflow_id}}

        result = graph.invoke(state,config=config)

        #result = graph.invoke(state)

        return {
            "lead_id": result["lead_id"],
            "conversation_id": result["conversation_id"],
            "next_question": result["next_question"],
            "workflow_id": workflow_id,
        }
    
    def continue_workflow(self, workflow_id: str, answer: str,):

        config = {"configurable": {"thread_id": workflow_id}}

        print("=============THREAD ID===========")
        print(workflow_id)
        print("==============STATE BEFORE RESUME===============")
        print(graph.get_state(config))

        #For an interrupted graph, you should not pass a new state.
        #state = {"patient_answer": answer}
        #result = graph.invoke(state, config=config,)

        #You should resume the interrupt itself
        result = graph.invoke(Command(resume=answer), config=config,)

        return result