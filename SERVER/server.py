from fastapi import FastAPI, UploadFile, File, HTTPException
import requests
import pandas as pd

class BaubuddyAPIHandler:
    def __init__(self):
        self.app = FastAPI()

        url = "https://api.baubuddy.de/index.php/login"
        payload = {
            "username": "365",
            "password": "1"
        }
        headers = {
            "Authorization": "Basic QVBJX0V4cGxvcmVyOjEyMzQ1NmlzQUxhbWVQYXNz",
            "Content-Type": "application/json"
        }
        response = requests.request("POST", url, json=payload, headers=headers)
        response.raise_for_status()
        self.API_BASE_URL = "https://api.baubuddy.de/index.php/v1"
        self.HEADERS = {
            "Authorization": f"Bearer {response.json()['oauth']['access_token']}",
            "Content-Type": "application/json"
        }

        @self.app.post("/process_csv/")
        async def process_csv(file: UploadFile = File(...)):
            try:
                df = pd.read_csv(file.file)

                active_vehicles = requests.get(f"{self.API_BASE_URL}/vehicles/select/active", headers=self.HEADERS).json()

                merged_data = pd.merge(df, pd.DataFrame(active_vehicles), on="vehicleId", how="inner")

                merged_data = merged_data.dropna(subset=["hu"])

                label_ids = merged_data["labelIds"].explode().unique()
                color_codes = {}
                for label_id in label_ids:
                    label_info = requests.get(f"{self.API_BASE_URL}/labels/{label_id}", headers=self.HEADERS).json()
                    color_codes[label_id] = label_info["colorCode"]

                merged_data["colorCode"] = merged_data["labelIds"].apply(lambda x: [color_codes[l] for l in x])

                result = merged_data.to_dict(orient="records")

                return result

            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

    def start_server(self):
        import uvicorn
        uvicorn.run(self.app, host="0.0.0.0", port=8000)

    def process_csv(self, csv_file_path, keys=None, colored=False):
        try:
            with open(csv_file_path, "rb") as file:
                files = {"file": file}
                response = requests.post(f"{self.API_BASE_URL}/process_csv/", files=files, headers=self.HEADERS)
                response.raise_for_status()
                return response.json()

        except Exception as e:
            raise e

    def get_access_token(self):
        url = "https://api.baubuddy.de/index.php/login"
        payload = {
            "username": "365",
            "password": "1"
        }
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        response.raise_for_status()
        return response.json()["oauth"]["access_token"]