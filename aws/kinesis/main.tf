resource "aws_kinesis_stream" "input_data_stream" {
  name             = "stations"
  shard_count      = 1
  retention_period = 24
  tags = {
    Environment = "prod"
  }
}
