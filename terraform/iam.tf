resource "aws_iam_user" "connect_s3_writer" {
  name = "corepay-connect-s3-writer"
}

resource "aws_iam_policy" "connect_s3_write_policy" {
  name        = "corepay-connect-s3-write-policy"
  description = "Least-privilege: allows writing only to the corepay bronze bucket"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.bronze.arn,
          "${aws_s3_bucket.bronze.arn}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_user_policy_attachment" "attach" {
  user       = aws_iam_user.connect_s3_writer.name
  policy_arn = aws_iam_policy.connect_s3_write_policy.arn
}
