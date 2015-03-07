{
  "AWSTemplateFormatVersion" : "2010-09-09",

  "Description" : "Hello World Example show you how to use agile_conf to create cloudformation template.",

    "Mappings": {
    "InstanceSecurityGroup": {{ subnet_security_groups|jsonify }},
    "EC2Instance" : {
      "Type" : "AWS::EC2::Instance",
      "Properties" : {
          "IamInstanceProfile": {
              "Ref": "InstanceProfile"
          }, 
          "ImageId": "{{ image_id }}", 
          "InstanceType": "{{ instance_type }}", 
          "KeyName": "{{ key_name }}", 
          "SubnetId": "{{ subnet_id[ conf.name ] }}",
          "SecurityGroupIds": {
              "Fn::FindInMap": [
                  "InstanceSecurityGroup", 
                  "{{ subnet_sg_group }}"
              ]
          },
          "UserData": {{ [_BUILD_DST_FOLDER, "0_userdata.sh"] |aws_userdata }},
          "Tags": {{ tags|jsonify }}
      }
    }
  },

  "Outputs" : {
    "InstanceId" : {
      "Description" : "InstanceId of the newly created EC2 instance",
      "Value" : { "Ref" : "EC2Instance" }
    },
    "AZ" : {
      "Description" : "Availability Zone of the newly created EC2 instance",
      "Value" : { "Fn::GetAtt" : [ "EC2Instance", "AvailabilityZone" ] }
    }
  }
}