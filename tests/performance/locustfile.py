from locust import HttpUser, task, between

class LoginUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def login(self):
        self.client.post("/auth/login/", json={
            "email": "dishurockstar456@gmail.com",
            "password": "Dishu123@"
        })
