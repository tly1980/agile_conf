DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

STACK_NAME={{project.product_fullname}}

echo "about to create stack: ${STACK_NAME}"

aws cloudformation create-stack \
	--stack-name ${STACK_NAME} \
	--template-body file://${DIR}/cfn/ec2.json \
	--capabilities CAPABILITY_IAM
