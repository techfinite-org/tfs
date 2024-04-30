def send_token_via_sms(otpsecret, token=None, phone_no=None):
	"""Send token as sms to user."""
	try:
		from frappe.core.doctype.sms_settings.sms_settings import send_request
	except Exception:
		return False

	if not phone_no:
		return False

	ss = frappe.get_doc("SMS Settings", "SMS Settings")
	if not ss.sms_gateway_url:
		return False

	hotp = pyotp.HOTP(otpsecret)
	inbuild_template = frappe.db.get_value("Inbuild Notification",{'method':'Login Verification','type':'SMS'},'message')
	template = f"Your verification code is {hotp.at(int(token))}" if not inbuild_template else f"{inbuild_template}{hotp.at(int(token))}"
	args = {ss.message_parameter:template}
	for d in ss.get("parameters"):
		args[d.parameter] = d.value

	args[ss.receiver_parameter] = phone_no

	sms_args = {"params": args, "gateway_url": ss.sms_gateway_url, "use_post": ss.use_post}
	enqueue(
		method=send_request,
		queue="short",
		timeout=300,
		event=None,
		is_async=True,
		job_name=None,
		now=False,
		**sms_args,
	)
	return True


