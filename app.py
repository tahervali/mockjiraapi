from flask import Flask, request, jsonify
import random
import datetime
import uuid
import logging
import json

app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Mock data configurations
PROJECT_NAME = "MOCK"
TEAM_NAME = "Toasted Snow"
STATUSES = ["To Do", "In Progress", "Code Review", "Testing", "Done"]
PRIORITIES = ["High", "Medium", "Low"]
CATEGORIES = ["Bug", "Feature", "Task", "Improvement"]
GROUPS = ["Frontend", "Backend", "Infrastructure", "Design"]
SITES = ["Site A", "Site B", "Site C"]
USERS = ["John Doe", "Jane Smith", "Bob Johnson", "Alice Brown", "Charlie Wilson"]
base_url = "http://localhost:5000"
# base_url = "http://mockapigen-brheczbde3f6ewc2.centralindia-01.azurewebsites.net"
azuer_url = "http://mockapigen-brheczbde3f6ewc2.centralindia-01.azurewebsites.net"
# Storage for our mock data
issues = []
issue_history = {}

def generate_mock_issues(count=150):
    """Generate a specified number of mock Jira issues"""
    mock_issues = []
    
    for i in range(count):
        issue_id = str(uuid.uuid4())
        issue_key = f"{PROJECT_NAME}-{i+1}"
        
        # Create timestamps within the last 90 days
        days_ago = random.randint(0, 90)
        created_date = (datetime.datetime.now() - datetime.timedelta(days=days_ago)).isoformat()
        
        # 50% chance of having a due date
        due_date = None
        if random.random() > 0.5:
            due_days = random.randint(days_ago, days_ago + 30)
            due_date = (datetime.datetime.now() - datetime.timedelta(days=days_ago) + 
                         datetime.timedelta(days=due_days)).strftime("%Y-%m-%d")
        
        # Create the issue
        issue = {
            "id": issue_id,
            "key": issue_key,
            "fields": {
                "project": {"name": PROJECT_NAME},
                "customfield_10001": {"name": TEAM_NAME},
                "created": created_date,
                "creator": {"displayName": random.choice(USERS)},
                "reporter": {"displayName": random.choice(USERS)},
                "assignee": {"displayName": random.choice(USERS)},
                "status": {"name": random.choice(STATUSES)},
                "priority": {"name": random.choice(PRIORITIES)},
                "customfield_10078": {"value": random.choice(CATEGORIES)},
                "summary": f"Mock issue {i+1} for testing",
                "description": f"This is a detailed description for mock issue {i+1}",
                "customfield_10046": {"value": random.choice(GROUPS)},
                "customfield_10045": [{"value": random.choice(SITES)}],
                "duedate": due_date,
                "watches": {"self": f"{base_url}/rest/api/2/issue/{issue_key}/watchers"}
            }
        }
        
        mock_issues.append(issue)
        
        # Generate history for this issue
        generate_issue_history(issue_key)
    
    return mock_issues

def generate_issue_history(issue_key):
    """Generate mock history for a specific issue"""
    history = []
    
    # Start with "To Do"
    current_status = "To Do"
    
    # Between 0 and 5 status changes
    num_changes = random.randint(0, 5)
    
    for i in range(num_changes):
        # Get a new status different from the current one
        next_statuses = [s for s in STATUSES if s != current_status]
        if not next_statuses:
            break
            
        next_status = random.choice(next_statuses)
        
        # Create a timestamp for this change
        days_ago = random.randint(0, 80)  # Ensure it's within our 90-day window
        change_date = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days_ago)).isoformat()
        history.append({
            "Key": issue_key,
            "Author": random.choice(USERS),
            "DateTime": change_date,
            "FromStatus": current_status,
            "ToStatus": next_status
        })
        
        current_status = next_status
    
    issue_history[issue_key] = history

@app.route('/rest/api/2/serverInfo', methods=['GET'])
def server_info():
    """Mock endpoint for Jira server info - required by the JIRA library"""
    logger.info("Received server info request")
    
    response = {
        "baseUrl": base_url,
        "version": "8.13.5",
        "versionNumbers": [8, 13, 5],
        "deploymentType": "Server",
        "buildNumber": 813005,
        "buildDate": "2021-06-11T00:00:00.000+0000",
        "serverTime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000+0000"),
        "scmInfo": "mock-api-jira@github.com",
        "serverTitle": "Mock Jira API"
    }
    
    return jsonify(response)

@app.route('/rest/api/2/field', methods=['GET'])
def get_fields():
    """Mock endpoint for Jira fields - required by the JIRA library"""
    logger.info("Received fields request")
    
    fields = [
        {"id": "summary", "name": "Summary", "custom": False, "orderable": True, "navigable": True, "searchable": True},
        {"id": "description", "name": "Description", "custom": False, "orderable": True, "navigable": True, "searchable": True},
        {"id": "status", "name": "Status", "custom": False, "orderable": True, "navigable": True, "searchable": True},
        {"id": "project", "name": "Project", "custom": False, "orderable": True, "navigable": True, "searchable": True},
        {"id": "priority", "name": "Priority", "custom": False, "orderable": True, "navigable": True, "searchable": True},
        {"id": "customfield_10001", "name": "Team", "custom": True, "orderable": True, "navigable": True, "searchable": True},
        {"id": "customfield_10078", "name": "Category", "custom": True, "orderable": True, "navigable": True, "searchable": True},
        {"id": "customfield_10046", "name": "Group", "custom": True, "orderable": True, "navigable": True, "searchable": True},
        {"id": "customfield_10045", "name": "Site", "custom": True, "orderable": True, "navigable": True, "searchable": True}
    ]
    
    return jsonify(fields)

@app.route('/rest/api/2/myself', methods=['GET'])
def get_current_user():
    """Mock endpoint for current user info - required by the JIRA library"""
    logger.info("Received current user request")
    
    response = {
        "self": f"{base_url}/rest/api/2/user?username=test_user",
        "name": "test_user",
        "displayName": "Test User",
        "active": True,
        "timeZone": "UTC",
        "groups": {"size": 1, "items": [{"name": "jira-users"}]},
        "applicationRoles": {"size": 1, "items": [{"name": "jira-users"}]}
    }
    
    return jsonify(response)

@app.route('/rest/api/2/search', methods=['GET', 'POST'])
def search_issues():
    """Mock endpoint for Jira issue search - support for both GET and POST"""
    logger.info(f"Received search request: {request.method}")
    
    # Parse parameters based on request method
    if request.method == 'GET':
        jql = request.args.get('jql', '')
        start_at = int(request.args.get('startAt', 0))
        max_results = int(request.args.get('maxResults', 50))
        expand = request.args.get('expand', '')
    else:  # POST
        data = request.json
        jql = data.get('jql', '')
        start_at = int(data.get('startAt', 0))
        max_results = int(data.get('maxResults', 50))
        expand = data.get('expand', '')
    
    logger.info(f"JQL: {jql}, StartAt: {start_at}, MaxResults: {max_results}, Expand: {expand}")
    
    # For simplicity, we'll ignore the JQL and just return paginated results
    paginated_issues = issues[start_at:start_at + max_results]
    
    # If changelog is requested in expand, add it to each issue
    if 'changelog' in expand:
        for issue in paginated_issues:
            issue_key = issue['key']
            histories = []
            changes = issue_history.get(issue_key, [])
            
            for idx, change in enumerate(changes):
                history = {
                    "id": str(uuid.uuid4()),
                    "author": {"displayName": change["Author"]},
                    "created": change["DateTime"],
                    "items": [
                        {
                            "field": "status",
                            "fieldtype": "jira",
                            "from": f"{idx}",
                            "fromString": change["FromStatus"],
                            "to": f"{idx+1}",
                            "toString": change["ToStatus"]
                        }
                    ]
                }
                histories.append(history)
            
            issue["changelog"] = {
                "startAt": 0,
                "maxResults": 100,
                "total": len(histories),
                "histories": histories
            }
    
    response = {
        "expand": f"schema,names{',changelog' if 'changelog' in expand else ''}",
        "startAt": start_at,
        "maxResults": max_results,
        "total": len(issues),
        "issues": paginated_issues
    }
    
    return jsonify(response)

@app.route('/rest/api/2/issue/<issue_key>/watchers', methods=['GET'])
def get_watchers(issue_key):
    """Mock endpoint for Jira issue watchers"""
    logger.info(f"Received watchers request for issue: {issue_key}")
    
    # Generate 0-5 random watchers
    num_watchers = random.randint(0, 5)
    watchers = []
    
    for _ in range(num_watchers):
        watchers.append({
            "self": f"{base_url}/rest/api/2/user?username={uuid.uuid4()}",
            "name": f"user{random.randint(1, 100)}",
            "displayName": random.choice(USERS),
            "active": True
        })
    
    response = {
        "self": f"{base_url}/rest/api/2/issue/{issue_key}/watchers",
        "isWatching": False,
        "watchCount": len(watchers),
        "watchers": watchers
    }
    
    return jsonify(response)

@app.route('/rest/api/2/issue/<issue_key>', methods=['GET'])
def get_issue(issue_key):
    """Mock endpoint for getting a specific Jira issue with changelog"""
    logger.info(f"Received issue request: {issue_key}")
    
    # Find the issue or return 404
    found_issue = None
    for issue in issues:
        if issue['key'] == issue_key:
            found_issue = issue.copy()
            break
    
    if not found_issue:
        return jsonify({"error": "Issue not found"}), 404
    
    # Add changelog if requested
    expand = request.args.get('expand', '')
    if 'changelog' in expand:
        histories = []
        
        # Get history for this issue
        changes = issue_history.get(issue_key, [])
        
        for idx, change in enumerate(changes):
            history = {
                "id": str(uuid.uuid4()),
                "author": {"displayName": change["Author"]},
                "created": change["DateTime"],
                "items": [
                    {
                        "field": "status",
                        "fieldtype": "jira",
                        "from": f"{idx}",
                        "fromString": change["FromStatus"],
                        "to": f"{idx+1}",
                        "toString": change["ToStatus"]
                    }
                ]
            }
            histories.append(history)
        
        found_issue["changelog"] = {
            "startAt": 0,
            "maxResults": 100,
            "total": len(histories),
            "histories": histories
        }
    
    return jsonify(found_issue)

@app.route('/rest/api/2/project', methods=['GET'])
def get_projects():
    """Mock endpoint for getting projects"""
    logger.info("Received projects request")
    
    projects = [{
        "self": f"{base_url}/rest/api/2/project/10000",
        "id": "10000",
        "key": PROJECT_NAME,
        "name": PROJECT_NAME,
        "avatarUrls": {
            "48x48": f"{base_url}/secure/projectavatar?size=large&pid=10000",
            "24x24": f"{base_url}/secure/projectavatar?size=small&pid=10000",
            "16x16": f"{base_url}/secure/projectavatar?size=xsmall&pid=10000",
            "32x32": f"{base_url}/secure/projectavatar?size=medium&pid=10000"
        },
        "projectCategory": {
            "self": f"{base_url}/rest/api/2/projectCategory/10000",
            "id": "10000",
            "name": "MOCK Category",
            "description": "Mock Project Category"
        }
    }]
    
    return jsonify(projects)

@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    """Health check endpoint"""
    return jsonify({"status": "UP", "timestamp": datetime.datetime.now().isoformat()})

# Helper function to handle direct API calls for the JIRA library
@app.route('/rest/api/2/<path:subpath>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def api_catchall(subpath):
    """Catch-all handler for any other API endpoints not explicitly defined"""
    logger.warning(f"Received request for undefined endpoint: {subpath}")
    
    # Return a minimal valid response
    if subpath.startswith('issue'):
        # Try to extract issue key from path
        parts = subpath.split('/')
        if len(parts) > 1:
            issue_key = parts[1]
            # Find the issue
            for issue in issues:
                if issue['key'] == issue_key:
                    return jsonify(issue)
    
    # For any other endpoint, return a simple success response
    return jsonify({"status": "success", "message": f"Mock API doesn't fully implement {subpath}", "path": subpath})

# Initialize data with the app context
with app.app_context():
    issues = generate_mock_issues(150)
    logger.info(f"Initialized {len(issues)} mock Jira issues and their history")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)