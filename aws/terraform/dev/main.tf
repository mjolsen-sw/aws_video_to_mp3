# VPC and Networking configuration
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr_block
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name        = "Video-To-MP3 VPC"
    Environment = var.environment
  }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "IGW"
    Environment = var.environment
  }
}

resource "aws_subnet" "SubnetPub1" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.1.0/24"

  tags = {
    Name        = "SubnetPub1"
    Environment = var.environment
  }
}

resource "aws_subnet" "SubnetPub2" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.2.0/24"

  tags = {
    Name        = "SubnetPub2"
    Environment = var.environment
  }
}

resource "aws_subnet" "SubnetPriv1" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.3.0/24"

  tags = {
    Name        = "SubnetPriv1"
    Environment = var.environment
  }
}

resource "aws_subnet" "SubnetPriv2" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.4.0/24"

  tags = {
    Name        = "SubnetPriv2"
    Environment = var.environment
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name        = "PublicRouteTable"
    Environment = var.environment
  }
}

resource "aws_route_table_association" "pub1" {
  subnet_id      = aws_subnet.SubnetPub1.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "pub2" {
  subnet_id      = aws_subnet.SubnetPub2.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "priv1" {
  subnet_id      = aws_subnet.SubnetPriv1.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "priv2" {
  subnet_id      = aws_subnet.SubnetPriv2.id
  route_table_id = aws_route_table.public.id
}

