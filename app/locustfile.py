from locust import HttpUser, task, between

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyNSIsImV4cCI6MTc3MzE0NDUyNn0.urgkBRhM0B_L2OS890QFa8fOLWkcjKjmfcj8iKs-gZk"

class CodeExecutionUser(HttpUser):

    wait_time = between(1, 2)

    @task
    def run_code(self):

        payload = {
            "source_code": "import java.util.*;\npublic class Main{\npublic static void main(String[] args){\nScanner sc=new Scanner(System.in);\nint n=sc.nextInt();\nint[] height=new int[n];\nfor(int i=0;i<n;i++)height[i]=sc.nextInt();\nint left=0,right=n-1,leftMax=0,rightMax=0,water=0;\nwhile(left<right){\nif(height[left]<height[right]){\nif(height[left]>=leftMax)leftMax=height[left];\nelse water+=leftMax-height[left];\nleft++;\n}else{\nif(height[right]>=rightMax)rightMax=height[right];\nelse water+=rightMax-height[right];\nright--;\n}\n}\nSystem.out.print(water);\n}\n}",
            "language_id": 62,
            "problem_id": 35
            }

        self.client.post(
        "/api/v2/execution/submit",
        json=payload,
        cookies={"access_token": TOKEN}
    )