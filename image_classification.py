from azure.cognitiveservices.vision.customvision.training import training_api
from azure.cognitiveservices.vision.customvision.training.models import ImageUrlCreateEntry
from azure.cognitiveservices.vision.customvision.prediction import prediction_endpoint
from azure.cognitiveservices.vision.customvision.prediction.prediction_endpoint import models
import time

###################################### 1. Access an existing Custom Vision Service project ######################################

# Replace with a valid key
training_key = "67aab0c30d9c4e2d806b5d5e6e80ca57"
prediction_key = "dcba629f05724d61a3b0b3c58f7c18c6"
project_id = "a7ceb1ee-630f-403f-8fe7-f68e8e914233"

trainer = training_api.TrainingApi(training_key)

# Access an existing project
print ("Access an existing project...")
project = trainer.get_project(project_id)


###################################### 2. Access tags to project ################################################################


# Access tags in existing project
print ("Access tags...")
tags = trainer.get_tags(project.id)
Hemlock_tag_count = 0
JapaneseCherry_tag_count = 0

# Loop all tags to find tags to be used
for index in range(len(tags)):
	print("The tag name is " + tags[index].name)
	print("The tag id is " + tags[index].id)

	if (tags[index].name == "Hemlock"):
		Hemlock_tag_count = 1
		hemlock_tag = tags[index]
	elif (tags[index].name == "Japanese Cherry"):
		JapaneseCherry_tag_count = 1
		cherry_tag = tags[index]

# Make two tags in the new project (if the tags are not found)
if Hemlock_tag_count == 0:
	hemlock_tag = trainer.create_tag(project.id, "Hemlock")
	print("Creating Tag Hemlock")
if JapaneseCherry_tag_count == 0:
	cherry_tag = trainer.create_tag(project.id, "Japanese Cherry")
	print("Creating Tag Japanese Cherry")


###################################### 3. Upload images to the project ##########################################################
base_image_url = "https://raw.githubusercontent.com/Microsoft/Cognitive-CustomVision-Windows/master/Samples/"

print ("Adding images...")
for image_num in range(1,10):
    image_url = base_image_url + "Images/Hemlock/hemlock_{}.jpg".format(image_num)
    trainer.create_images_from_urls(project.id, [ ImageUrlCreateEntry(url=image_url, tag_ids=[ hemlock_tag.id ] ) ])

for image_num in range(1,10):
    image_url = base_image_url + "Images/Japanese Cherry/japanese_cherry_{}.jpg".format(image_num)
    trainer.create_images_from_urls(project.id, [ ImageUrlCreateEntry(url=image_url, tag_ids=[ cherry_tag.id ] ) ])


# Alternatively, if the images were on disk in a folder called Images alongside the sample.py, then
# they can be added by using the following:
#
#import os
#hemlock_dir = "Images\\Hemlock"
#for image in os.listdir(os.fsencode("Images\\Hemlock")):
#    with open(hemlock_dir + "\\" + os.fsdecode(image), mode="rb") as img_data: 
#        trainer.create_images_from_data(project.id, img_data, [ hemlock_tag.id ])
#
#cherry_dir = "Images\\Japanese Cherry"
#for image in os.listdir(os.fsencode("Images\\Japanese Cherry")):
#    with open(cherry_dir + "\\" + os.fsdecode(image), mode="rb") as img_data: 
#        trainer.create_images_from_data(project.id, img_data, [ cherry_tag.id ])



###################################### 4. Training project ######################################################################
print ("Training...")
iteration = trainer.train_project(project.id)
while (iteration.status != "Completed"):
    iteration = trainer.get_iteration(project.id, iteration.id)
    print ("Training status: " + iteration.status)
    time.sleep(1)

# The iteration is now trained. Make it the default project endpoint
trainer.update_iteration(project.id, iteration.id, is_default=True)
print ("Done!")



###################################### 5. Predict object ########################################################################

# Now there is a trained endpoint that can be used to make a prediction
predictor = prediction_endpoint.PredictionEndpoint(prediction_key)

test_img_url = base_image_url + "Images/Test/test_image.jpg"
results = predictor.predict_image_url(project.id, iteration.id, url=test_img_url)

# Alternatively, if the images were on disk in a folder called Images alongside the sample.py, then
# they can be added by using the following.
#
# Open the sample image and get back the prediction results.
# with open("Images\\test\\test_image.jpg", mode="rb") as test_data:
#     results = predictor.predict_image(project.id, test_data, iteration.id)

# Display the results.
for prediction in results.predictions:
    print ("\t" + prediction.tag_name + ": {0:.2f}%".format(prediction.probability * 100))
