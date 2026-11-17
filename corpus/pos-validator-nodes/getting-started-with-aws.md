
# Getting Started With AWS

## Create an AWS Account

AWS (Amazon Cloud) account creation Prerequisites:

* Credit card
* Landline or mobile phone
* Navigate to the [<mark style="color:blue;">AWS official website</mark>](https://aws.amazon.com/) and click the “Sign Up” button.
* Fill in all registration information including your personal information and credit card details.
* Next, the system will call to confirm your phone number. Enter the 4-digit number (ending with #) displayed on the computer screen.
* If the account was successfully created, your card will be charged for $1 as part of the verification process (this will be refunded later).

## Create a Suitable EC2 Virtual Machine

EC2 virtual machine set up

**1. Create an AWS EC2 instance**

Log in to the [<mark style="color:blue;">EC2 console</mark>](https://console.aws.amazon.com/ec2/):

Select the location of the machine in the upper right corner:

![](https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2FDQRaBt9EDVbqz7gNq7Hs%2Fstaking1.png?alt=media\&token=36e52103-75bc-4561-9f03-406517b11f7d)

Find “Instances” in the menu on the left side of the page

![](https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2F6fjYOBiU2bICmKrX5PEi%2Fstaking2.png?alt=media\&token=36268cac-ad53-4599-9874-fd4a880e833f)

Then click on the “Launch Instance” button:

![](https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2Fv6OTJGNe9LjkXyOZ3TpB%2Fstaking3.png?alt=media\&token=7eee70b3-8e74-4a45-8532-371b5eb8f1a2)

Choose an Amazon system image: Ubuntu 22.04 is recommended

![](https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2FTbf25ALKjNAo5k0LD06t%2Fstaking4.png?alt=media\&token=6ec950f7-cb1e-4c9d-9a04-7e0f99a50e34)

Select the instance type. We recommend the m4.large configuration.

![](https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2FTSx056FcnScyOLZo5NZV%2Fstaking5.png?alt=media\&token=d4d51eb6-915b-4995-ba88-131d613fd238)

Click the “Next: Configure Instance Details” button and input the following default configuration:

![](https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2FEqmMOdEmlCWR9InFiR50%2Fstaking6.png?alt=media\&token=2ca48ed5-e299-4ef8-b5dc-fbaa3098d599)

Click the “Next: Add Storage” button

The recommended setting is 80GB

![](https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2FIRORp2z4mcFT9MXVAYpn%2Fstaking7.png?alt=media\&token=c5b3cb71-9ea2-4940-b20e-1d09f46de42f)

Click the “Next: Add Tags” button to add tags for easy recall:

![](https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2FC0ZdNp1yn0B2PkEPxM6L%2Fstaking8.png?alt=media\&token=c2837228-74bd-4cfa-9acd-b1110382b179)

Click the “Next: Configure Security Group” button

Add firewall rule and then click the “Review and Launch” button to verify the instance:

![](https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2FLqjKGXbj5m7yTsiQVQCd%2Fstaking9.png?alt=media\&token=00457d02-2885-4812-b629-f1eb695811f8)

Click the “Launch” button to launch the instance

![](https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2FRSf3QeLQ5x72n0dGOgUc%2Fstaking10.png?alt=media\&token=bdb94a2b-efe6-43c2-a342-f5551c3cbc73)

Create a key, download the key pair and keep it in a safe place. You will use this key when logging in with SSH.

![](https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2FstcDvvZKmBMdo3PXXARW%2Fstaking11.png?alt=media\&token=34beb1f5-685d-4fe9-813a-cb2e0fd590fc)

That completes the EC2 instance creation.

## SSH login to AWS EC2

To use the SSH login method under Linux, set the key file permissions with the following command (make sure to replace `your_keyfile.pem` with whatever you named your key file):

```
chmod 400 your_keyfile.pem  
```

SSH login command (make sure to replace `your_EC2_ip_address` with your EC2 instance's IPv4 Public IP address:

```
ssh -i your_keyfile.pem ubuntu@your_EC2_ip_address
```

Windows users should use PuTTY to SSH in, see Amazon's [instructions](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/putty.html).

Now you are finished. If you would like set up a validator node, please follow the instructions here.

## How to Delete an EC2 instance

First terminate the instance:

![](https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2F00bHq7TO7XHr3wTLxweV%2Fstaking12.png?alt=media\&token=5352b512-f014-4751-82fa-03dca3231192)

Confirm termination:

![](https://1201656741-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FEn9ZUm7B1LreudyM5sLh%2Fuploads%2FWikpT29skgv23oM1YhVd%2Fstaking13.png?alt=media\&token=f752c644-1ac5-4b25-b388-79c62cbaa9b7)

After termination, check that the volume has been deleted to avoid any costs. In addition, the instance will remain in the list for a while after termination, and will generally disappear within half an hour.
