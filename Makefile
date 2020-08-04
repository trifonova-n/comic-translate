
deploy: deploy_gcfunction deploy_model deploy_web test_gcfunction

gcf_files := $(wildcard comic/*.py) $(wildcard comic/models/*.py) $(wildcard comic/utils/*.py) \
$(wildcard comic/vis/*.py) $(wildcard gcfunction/*.py) $(wildcard gcfunction/*.txt)

deploy_gcfunction: $(gcf_files)
	rm -rf deployed
	mkdir deployed
	mkdir deployed/comic
	mkdir deployed/comic/models
	mkdir deployed/comic/utils
	mkdir deployed/comic/vis
	cp comic/*.py deployed/comic/
	cp comic/models/*.py deployed/comic/models/
	cp comic/utils/*.py deployed/comic/utils/
	cp comic/vis/*.py deployed/comic/vis/
	cp gcfunction/*.py deployed/
	cp gcfunction/*.txt deployed/

	gcloud functions deploy detect_text --source=./deployed --runtime=python37 --stage-bucket comic-translate \
	--trigger-http --memory=2048
	echo "" > $@

deploy_model: requirements.txt
	gsutil cp model/text_detector.pth gs://comic-translate/models/text_detector.pth
	echo "" > $@

web_files := $(wildcard web/*.html) $(wildcard web/js/*.js)
deploy_web: $(web_files)
	gsutil cp -r web/* gs://comic-translate.com
	echo "" > $@

test_gcfunction:
	gcloud functions call detect_text --data='{"image_url": "http://comic-translate.com/test/text_image.jpg"}'
