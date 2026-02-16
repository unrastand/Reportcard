# Payment functionality is disabled for SQLite setup
def online_admission_sslpayment(request, pk):
    return HttpResponse("Payment functionality is not available in this SQLite setup.")
