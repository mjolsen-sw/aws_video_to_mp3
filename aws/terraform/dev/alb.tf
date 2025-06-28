resource "aws_lb" "private_alb" {
  name               = "video-to-mp3-private-alb"
  internal           = true
  load_balancer_type = "application"
  subnets            = [
    aws_subnet.SubnetPriv1.id,
    aws_subnet.SubnetPriv2.id
  ]
  security_groups    = [aws_security_group.alb_sg.id]

  tags = {
    Name        = "PrivateALB"
    Environment = var.environment
  }
}

resource "aws_security_group" "alb_sg" {
  name        = "alb-sg"
  description = "Allow HTTP for ALB"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Adjust as needed for your use case
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "ALBSG"
    Environment = var.environment
  }
}

resource "aws_lb_target_group" "app_tg" {
  name     = "video-to-mp3-app-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id

  health_check {
    path                = "/"
    protocol            = "HTTP"
    matcher             = "200-399"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }

  tags = {
    Name        = "AppTG"
    Environment = var.environment
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.private_alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app_tg.arn
  }
}