DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
STACK_NAME={{project.product_fullname}}

echo "about to kill stack ${STACK_NAME}"

aws cloudformation delete-stack \
	--stack-name $STACK_NAME \
