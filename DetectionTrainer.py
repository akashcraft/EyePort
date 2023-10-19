from imageai.Detection.Custom import DetectionModelTrainer

trainer = DetectionModelTrainer()
trainer.setModelTypeAsYOLOv3()
trainer.setDataDirectory(data_directory="Ocean")
trainer.setTrainConfig(object_names_array=["iceberg","boat","ship"]
                       , batch_size=5, num_experiments=500, train_from_pretrained_model="yolov3.pt")
trainer.trainModel()
