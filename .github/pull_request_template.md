## Description

Please include a summary of change and which issue is fixed. Please also include relevant motivation and context. List any dependencies that are required for this change.

## Checklist

- [ ] Generate non-chunked keys and upload them to s3.
- [ ] Update these args in Dockerfile
  - [ ] ARG ZKP2P_BRANCH_NAME=xxxxxx
  - [ ] ARG ZKP2P_VERSION=xxxxxx
  - [ ] ARG PROVER_API_BRANCH_NAME=xxxxxx
- [ ] Commit the changes in prover-api
- [ ] Build the docker file image on an AWS machine.
  - `sudo docker build -t 0xsachink/zkp2p:modal-0.0.x .`
- [ ] Publish the docker image file to dockerhub.
  - `sudo docker push 0xsachink/zkp2p:modal-0.0.x`
- [ ] Update the docker file version in prover/api.py. Also, increment the version in the stub name.
- [ ] Serve the app using modal serve app.py.
- [ ] Update the MODAL ENDPOINT link in the .env
- [ ] Run python api.py to test the proof generation works!
- [ ] Deploy the app using modal deploy app.py
