import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import requests
import json
import os
from django.conf import settings


class GlobalImageClassifier:
    _instance = None
    _model = None
    _labels = None
    _preprocess = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GlobalImageClassifier, cls).__new__(cls)
            cls._instance.initialize_model()
        return cls._instance

    def initialize_model(self):
        print("Loding MobileNetV2...")
        try:

            self._model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)
            self._model.eval()

            self._preprocess = transforms.Compose([
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ])

            self._labels = self.load_labels()
            print('Succefully!')
        except Exception as e:
            print('Error: {e}')

    def load_labels(self):
        path = os.path.join(settings.BASE_DIR, 'media', 'models', 'imagenet_classes.json')
        os.makedirs(os.path.dirname(path), exist_ok=True)

        if not os.path.exists(path):
            url = "https://raw.githubusercontent.com/anishathalye/imagenet-simple-labels/master/imagenet-simple-labels.json"
            try:
                r = requests.get(url)
                with open(path, 'w') as f:
                    f.write(r.text)
            except:
                return []

        with open(path, 'r') as f:
            return json.load(f)

    def predict_from_file_object(self, file_obj):
        if self._model is None:
            return {"success": False, "error": "Model failed to load"}

        try:
            img = Image.open(file_obj).convert('RGB')

            input_tensor = self._preprocess(img).unsqueeze(0)

            with torch.no_grad():
                output = self._model(input_tensor)

            probabilities = torch.nn.functional.softmax(output[0], dim=0)
            score, idx = torch.topk(probabilities, 1)

            idx_val = idx.item()
            name = self._labels[idx_val] if self._labels and idx_val < len(self._labels) else "Unknown"

            return {
                "success": True,
                "product_name": name.title(),
                "confidence": round(score.item() * 100, 2)
            }

        except Exception as e:
            return {"success": False, "error": str(e)}