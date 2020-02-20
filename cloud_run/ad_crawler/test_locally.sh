
# Build and run docker locally
docker build -t adcrawler .
docker run --rm -p 8080:8080 -e PORT=8080 adcrawler

# Push docker image to cloud
docker tag [SOURCE_IMAGE] [HOSTNAME]/[PROJECT-ID]/[IMAGE]
docker push [HOSTNAME]/[PROJECT-ID]/[IMAGE]


# To run scrapy directly:
scrapy crawl finn_ads -a "url=https://www.finn.no/realestate/homes/search.html?location=0.20061&page=2"

# Send POST request:
curl -d '{"url":"https://www.finn.no/realestate/homes/search.html?location=0.20061&page=2"}' -H "Content-Type: application/json" -X POST http://localhost:8080/