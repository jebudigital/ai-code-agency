#!/usr/bin/env python3
"""
AI Coding Agency - Demo Script

This script demonstrates the capabilities of the AI coding agency system.
Run it to see how the multi-agent system works together.
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path so we can import agents
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Now import from agents package
from agents.project_manager import ProjectManagerAgent

def demo_basic_functionality():
    """Demonstrate basic agent functionality"""
    print("🚀 AI Coding Agency Demo")
    print("=" * 50)
    
    # Create a temporary project directory
    demo_dir = Path("demo_project")
    demo_dir.mkdir(exist_ok=True)
    
    try:
        # Initialize the project manager
        print("📋 Initializing AI Coding Agency...")
        pm = ProjectManagerAgent(project_path=str(demo_dir))
        print("✅ Project Manager initialized successfully!")
        
        # Create a simple project
        print("\n📝 Creating a sample project...")
        project_id = pm.create_project(
            title="Hello World API",
            requirements="""
            Create a simple REST API that:
            1. Has a /hello endpoint that returns "Hello, World!"
            2. Has a /health endpoint for health checks
            3. Uses Flask framework
            4. Includes basic error handling
            5. Has unit tests
            6. Includes a README with setup instructions
            
            The API should be production-ready and well-documented.
            """
        )
        
        print(f"✅ Project created with ID: {project_id}")
        
        # Show project plan
        print("\n📊 Project Plan:")
        plan = pm.project_plans[project_id]
        print(f"   Name: {plan.project_name}")
        print(f"   Timeline: {plan.timeline_days} days")
        print(f"   Estimated Hours: {plan.total_estimated_hours}")
        print(f"   Tasks: {len(plan.tasks)}")
        
        for task in plan.tasks:
            print(f"     - {task.title} ({task.agent}) - {task.priority} priority")
        
        # Show project status
        print("\n📈 Project Status:")
        status = pm.get_project_status(project_id)
        print(f"   Status: {status.status}")
        print(f"   Progress: {status.progress_percentage:.1f}%")
        print(f"   Current Task: {status.current_task}")
        
        print("\n🎯 This demo shows the planning phase of the AI Coding Agency.")
        print("   To see the full execution, run: python main.py --execute-project", project_id)
        
        return project_id
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return None

def demo_agent_capabilities():
    """Demonstrate individual agent capabilities"""
    print("\n🔧 Individual Agent Capabilities Demo")
    print("=" * 50)
    
    demo_dir = Path("demo_agents")
    demo_dir.mkdir(exist_ok=True)
    
    try:
        from agents.coder import CoderAgent
        from agents.doc_agent import DocumentationAgent
        
        # Test Coder Agent
        print("💻 Testing Coder Agent...")
        coder = CoderAgent(project_path=str(demo_dir))
        
        # Test file operations
        coder.use_tool('file_system', 'write_file', 'test.py', 'print("Hello from AI Coder!")')
        content = coder.use_tool('file_system', 'read_file', 'test.py')
        print(f"   ✅ File operations: {content}")
        
        # Test Documentation Agent
        print("📚 Testing Documentation Agent...")
        doc_agent = DocumentationAgent(project_path=str(demo_dir))
        
        # Create a simple project info
        project_info = {
            'name': 'Demo Project',
            'type': 'Python',
            'languages': ['Python'],
            'dependencies': ['flask', 'requests']
        }
        
        # Generate README
        readme = doc_agent.generate_readme(project_info)
        if readme:
            print("   ✅ README generation: Success")
            # Save a sample
            (demo_dir / 'README.md').write_text(readme)
        else:
            print("   ⚠️  README generation: No response (Ollama may not be running)")
        
        print("✅ Agent capabilities demo completed!")
        
    except Exception as e:
        print(f"❌ Agent demo failed: {e}")

def main():
    """Main demo function"""
    print("🤖 Welcome to the AI Coding Agency Demo!")
    print("This will demonstrate the multi-agent system capabilities.")
    print()
    
    # Check if Ollama is available
    try:
        import requests
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.ok:
            models = response.json().get('models', [])
            if models:
                print(f"✅ Ollama is running with {len(models)} model(s)")
                for model in models:
                    print(f"   - {model['name']} ({model['size']})")
            else:
                print("⚠️  Ollama is running but no models installed")
                print("   Run: ollama pull phind-codellama:34b-v2")
        else:
            print("❌ Ollama service not responding")
            print("   Make sure Ollama is running: ollama serve")
    except:
        print("❌ Cannot connect to Ollama")
        print("   Please start Ollama first: ollama serve")
        print("   Then install models: ollama pull phind-codellama:34b-v2")
        return
    
    print()
    
    # Run demos
    project_id = demo_basic_functionality()
    
    if project_id:
        demo_agent_capabilities()
        
        print("\n🎉 Demo completed successfully!")
        print(f"📁 Check the 'demo_project' directory for the created project")
        print(f"📁 Check the 'demo_agents' directory for agent demonstrations")
        print()
        print("🚀 To run the full AI Coding Agency:")
        print("   python main.py --interactive")
        print()
        print("📚 For more information, see the README.md file")

if __name__ == "__main__":
    main()
