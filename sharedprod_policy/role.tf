resource "aws_iam_role" "aws_role" {
    name = "Insert-Role-Name-Here"
    assume_role_policy = "${file("NameOfRole.json")}"
}

resource "aws_iam_policy" "aws_policy" {
    name = "Insert-Policy-Name-Here"
    assume_role_policy = "${file("NameOfPolicy.json")}"
}

resource "aws_iam_policy_attachment" "aws_attach" {
    name =  "aws_attachment"
    roles = ["${aws_iam_role.aws_role.name}"]
    policy_arn = "${aws_iam_policy.aws_policy.name}"
}

resource "aws_iam_policy" "aws_scan_policy" {
    name = "Insert-Scan-Policy-Name-Here"
    assume_role_policy = "${file("NameOfScanPolicy.json")}"
}

resource "aws_iam_policy_attachment" "aws_attach" {
    name =  "aws_attachment"
    roles = ["${aws_iam_role.aws_role.name}"]
    policy_arn = "${aws_iam_policy.aws_scan_policy.name}"
}