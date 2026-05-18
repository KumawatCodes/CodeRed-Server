variable "region" {
  default     = "ap-south-1"
  description = "AWS region - Mumbai (closest to India)"
}

variable "instance_type" {
  default     = "t3.micro"
  description = "t3.micro is free tier eligible for your account"
}