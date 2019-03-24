BINARY_MARKDOWN=$(curl --request POST --header "PRIVATE-TOKEN:$PRIVATE_TOKEN" --form "file=@./dist/$BINARY_NAME" $CI_API_V4_URL/projects/$CI_PROJECT_ID/uploads --verbose| jq -r '.markdown')


curl --header 'Content-Type:application/json' --header "PRIVATE-TOKEN:$PRIVATE_TOKEN" --data '{"name":'"$CI_COMMIT_TITLE"', "tag_name":'"$CI_COMMIT_TAG"', "description":'"$BINARY_MARKDOWN"' }' --request POST $CI_API_V4_URL/projects/$CI_PROJECT_ID/releases --verbose
