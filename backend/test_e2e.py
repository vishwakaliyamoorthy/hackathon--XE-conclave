import asyncio
import httpx
import time
import os

BASE_URL = "http://localhost:8000/api"

async def run_test():
    print("=== STARTING END-TO-END TEST ===")
    
    # Wait for server to be up
    async with httpx.AsyncClient() as client:
        for _ in range(10):
            try:
                r = await client.get("http://localhost:8000/")
                if r.status_code == 200:
                    break
            except httpx.ConnectError:
                pass
            time.sleep(1)
            
        print("\nStep 1: Sign up & Login")
        # Ensure unique email
        email = f"test_{int(time.time())}@example.com"
        signup_data = {
            "email": email,
            "password": "Password123",
            "full_name": "Test User",
            "organization": "Test Org",
            "role": "pm"
        }
        res = await client.post(f"{BASE_URL}/auth/signup", json=signup_data)
        if res.status_code != 201:
            print("Failed to sign up. Might already exist. Let's try login directly.")
            
        login_data = {"username": email, "password": "Password123"}
        res = await client.post(f"{BASE_URL}/auth/login", data=login_data)
        assert res.status_code == 200, f"Login failed: {res.text}"
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("-> Successfully authenticated.")
        
        print("\nStep 2: Upload Documents")
        files_prd = {"file": ("prd.txt", b"PRD: We need a User Login feature with Google Auth.", "text/plain")}
        data_prd = {"title": "Test PRD"}
        res = await client.post(f"{BASE_URL}/upload/prd", files=files_prd, data=data_prd, headers=headers)
        assert res.status_code == 201, f"PRD Upload failed: {res.text}"
        prd_id = res.json()["id"]
        print(f"-> PRD uploaded: {prd_id}")

        files_code = {"file": ("code.txt", b"Code: Implemented simple email/password auth.", "text/plain")}
        data_code = {"title": "Test Code"}
        res = await client.post(f"{BASE_URL}/upload/code", files=files_code, data=data_code, headers=headers)
        code_id = res.json()["id"]
        print(f"-> Code uploaded: {code_id}")
        
        print("\nStep 3: Create Analysis Session")
        session_data = {"title": "E2E Test Session"}
        res = await client.post(f"{BASE_URL}/analyze", json=session_data, headers=headers)
        assert res.status_code == 201
        analysis_id = res.json()["id"]
        print(f"-> Analysis session created: {analysis_id}")
        
        print("\nStep 4: Link Documents")
        link_data = {"prd_doc_id": prd_id, "code_doc_id": code_id}
        res = await client.post(f"{BASE_URL}/analyze/{analysis_id}/link-documents", json=link_data, headers=headers)
        assert res.status_code == 200
        print("-> Documents linked.")
        
        print("\nStep 5: Start Analysis")
        res = await client.post(f"{BASE_URL}/analyze/{analysis_id}/start", headers=headers)
        assert res.status_code == 200
        print("-> Analysis started.")
        
        print("\nStep 6: Polling for Results")
        for _ in range(30):
            res = await client.get(f"{BASE_URL}/analyze/{analysis_id}/results", headers=headers)
            data = res.json()
            if data.get("status") == "completed":
                print("-> Analysis completed successfully!")
                print(f"-> Conflicts found: {len(data.get('conflicts', []))}")
                break
            print("   Polling... (processing)")
            time.sleep(2)
        else:
            print("-> Polling timed out!")
            return
            
        print("\nStep 7: Approve Updates")
        approve_data = {"approved": True}
        res = await client.post(f"{BASE_URL}/analyze/{analysis_id}/approve", json=approve_data, headers=headers)
        assert res.status_code == 200, f"Approve failed: {res.text}"
        print(f"-> Approval response: {res.json()}")
        
        print("\n=== E2E TEST COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    asyncio.run(run_test())
