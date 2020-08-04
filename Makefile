
deploy: clean deploy_gcfunction deploy_model deploy_web

clean:
	rm -rf deployed

deploy_gcfunction: clean
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

deploy_model:
	gsutil cp model/text_detector.pth gs://comic-translate/models/text_detector.pth

deploy_web:
	gsutil cp -r web/* gs://comic-translate.com
