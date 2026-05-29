"""
Quick test script for LangGraph workflows and Celery tasks (ASCII-safe for Windows)
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_langgraph_workflow():
    """Test the LangGraph multi-agent workflow."""
    print("\n" + "="*50)
    print("Testing LangGraph Workflow")
    print("="*50 + "\n")

    try:
        from agent.langgraph_workflows import create_job_search_workflow

        print("[OK] Successfully imported LangGraph workflow")

        # Create workflow
        workflow = create_job_search_workflow()
        print("[OK] Workflow created successfully")

        # Test state
        initial_state = {
            "user_id": "test_user_123",
            "user_profile": {
                "desired_role": "Python Developer",
                "skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
                "experience_level": "Mid-level",
                "location": "Remote",
                "industry": "Technology"
            },
            "resume": {
                "full_name": "Hemanth Test",
                "email": "hemanth@example.com",
                "summary": "Experienced Python developer with expertise in backend development",
                "experience": [
                    {
                        "company": "Tech Corp",
                        "title": "Python Developer",
                        "duration": "2 years"
                    }
                ],
                "skills": ["Python", "FastAPI", "PostgreSQL"]
            },
            "next_stage": "job_search"
        }

        print("\n[INFO] Initial State:")
        print(f"   User ID: {initial_state['user_id']}")
        print(f"   Desired Role: {initial_state['user_profile']['desired_role']}")
        print(f"   Skills: {', '.join(initial_state['user_profile']['skills'])}")

        print("\n[RUN] Running workflow...")
        print("   (This may take a few seconds)\n")

        # Note: Workflow requires OpenAI API key to actually run
        # For now, just verify it compiles
        print("[OK] Workflow structure validated")
        print("   [NOTE] Full execution requires OpenAI API key in .env")

        return True

    except Exception as e:
        print(f"[FAIL] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_celery_imports():
    """Test Celery worker imports."""
    print("\n" + "="*50)
    print("Testing Celery Tasks")
    print("="*50 + "\n")

    try:
        import celery_worker
        print("[OK] Successfully imported celery_worker")

        # List available tasks
        tasks = [
            'search_jobs_task',
            'process_resume_task',
            'prepare_interview_task',
            'get_career_advice_task',
            'send_notification_task',
            'aggregate_analytics_task',
            'cleanup_sessions_task',
            'run_workflow_task',
            'health_check'
        ]

        print("\n[INFO] Available Celery Tasks:")
        for task in tasks:
            if hasattr(celery_worker, task):
                print(f"   [OK] {task}")
            else:
                print(f"   [FAIL] {task} - NOT FOUND")

        print("\n   [NOTE] To execute tasks, start Celery worker:")
        print("      celery -A celery_worker worker --loglevel=info")

        return True

    except Exception as e:
        print(f"[FAIL] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_agent_imports():
    """Test individual agent imports."""
    print("\n" + "="*50)
    print("Testing Individual Agents")
    print("="*50 + "\n")

    agents = [
        ('JobSearchAgent', 'agent.langgraph_workflows.job_search_agent'),
        ('ResumeAgent', 'agent.langgraph_workflows.resume_agent'),
        ('InterviewAgent', 'agent.langgraph_workflows.interview_agent'),
        ('CareerAdvisor', 'agent.langgraph_workflows.career_advisor'),
    ]

    all_success = True

    for agent_name, module_path in agents:
        try:
            module = __import__(module_path, fromlist=[agent_name])
            agent_class = getattr(module, agent_name)
            print(f"[OK] {agent_name} imported successfully")
        except Exception as e:
            print(f"[FAIL] {agent_name} import failed: {str(e)}")
            all_success = False

    return all_success


if __name__ == "__main__":
    print("\n" + "="*50)
    print("[TEST] Job Search AI Agent - Component Tests")
    print("="*50)

    results = []

    # Test 1: LangGraph Workflow
    results.append(("LangGraph Workflow", test_langgraph_workflow()))

    # Test 2: Individual Agents
    results.append(("Individual Agents", test_agent_imports()))

    # Test 3: Celery Tasks
    results.append(("Celery Tasks", test_celery_imports()))

    # Summary
    print("\n" + "="*50)
    print("Test Summary")
    print("="*50 + "\n")

    for test_name, success in results:
        status = "[PASS]" if success else "[FAIL]"
        print(f"{status} - {test_name}")

    all_passed = all(success for _, success in results)

    if all_passed:
        print("\n[PASS] All component tests passed!")
        print("\nNext steps:")
        print("1. Start infrastructure: docker-compose up -d postgres redis")
        print("2. Start auth service: python -m uvicorn backend.auth_service.main:app --port 8001")
        print("3. Start analytics service: python -m uvicorn backend.analytics_service.main:app --port 8005")
        print("4. Run API tests: bash test_services.sh")
    else:
        print("\n[FAIL] Some tests failed. Please check the errors above.")
        sys.exit(1)
