class PlannerAgent:
    def __init__(self):
        pass
    def plan(self, title: str, body: str):
        tasks = []
        tasks.append({'id':1,'title':f'Implement: {title}','description': body or 'Implement feature'})
        tasks.append({'id':2,'title':'Add unit tests','description':'Write pytest unit tests for the feature'})
        tasks.append({'id':3,'title':'Docs','description':'Update README and changelog'})
        return tasks
