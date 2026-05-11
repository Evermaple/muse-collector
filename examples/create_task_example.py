#!/usr/bin/env python3
"""Example: Create a crawl task via API."""
import requests
import json

# API endpoint
API_BASE_URL = "http://localhost:8000"

def create_song_task():
    """Create a song crawl task."""
    url = f"{API_BASE_URL}/api/tasks"
    
    payload = {
        "app_id": "test_app",
        "task_type": "1",  # 1 = song
        "srcs": ["netease"],
        "target_ids": ["123456", "789012", "345678"]  # Example song IDs
    }
    
    print("Creating song crawl task...")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Task created successfully!")
        print(f"Task ID: {result['data']['task_id']}")
        return result['data']['task_id']
    else:
        print(f"\n❌ Failed to create task: {response.text}")
        return None


def get_task_status(task_id):
    """Get task status."""
    url = f"{API_BASE_URL}/api/tasks/{task_id}"
    
    print(f"\nQuerying task status: {task_id}")
    
    response = requests.get(url)
    
    if response.status_code == 200:
        result = response.json()
        task = result['data']
        print(f"\n📊 Task Status:")
        print(f"  Status: {task['task_status']} (1=waiting, 2=running, 3=success, 4=failed)")
        print(f"  Total: {task['item_cnt']}")
        print(f"  Success: {task['success_cnt']}")
        print(f"  Failed Reason: {task['failed_reason']}")
    else:
        print(f"\n❌ Failed to get task: {response.text}")


def list_tasks():
    """List all tasks."""
    url = f"{API_BASE_URL}/api/tasks"
    
    print("\nListing all tasks...")
    
    response = requests.get(url, params={"page": 1, "page_size": 10})
    
    if response.status_code == 200:
        result = response.json()
        data = result['data']
        print(f"\n📋 Total tasks: {data['total']}")
        print(f"Page: {data['page']}/{(data['total'] + data['page_size'] - 1) // data['page_size']}")
        
        for task in data['tasks']:
            print(f"\n  Task ID: {task['task_id']}")
            print(f"  Type: {task['task_type']}")
            print(f"  Status: {task['task_status']}")
            print(f"  Progress: {task['success_cnt']}/{task['item_cnt']}")
    else:
        print(f"\n❌ Failed to list tasks: {response.text}")


def main():
    """Main function."""
    print("=" * 60)
    print("Muse Collector API Example")
    print("=" * 60)
    
    # Check API health
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API is healthy\n")
        else:
            print("⚠️  API health check failed\n")
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print("Please make sure the API server is running (python main.py)")
        return
    
    # Create a task
    task_id = create_song_task()
    
    if task_id:
        # Get task status
        get_task_status(task_id)
    
    # List all tasks
    list_tasks()
    
    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
