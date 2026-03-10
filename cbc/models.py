from django.db import models


class MessageSpec(models.Model):

    sending_entity_in = models.CharField(max_length=100)

    transmitting_country = models.CharField(max_length=2, default="TN")

    receiving_country = models.CharField(max_length=2, default="TN")

    message_type = models.CharField(max_length=10, default="CBC")

    message_ref_id = models.CharField(max_length=200)

    reporting_period = models.IntegerField()

    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message_ref_id


class ReportingEntity(models.Model):

    name = models.CharField(max_length=200)

    tin = models.CharField(max_length=50)

    country_code = models.CharField(max_length=2, default="TN")

    address = models.CharField(max_length=300, blank=True)

    city = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name


class CbcBody(models.Model):

    message_spec = models.ForeignKey(MessageSpec, on_delete=models.CASCADE)

    reporting_entity = models.ForeignKey(ReportingEntity, on_delete=models.CASCADE)

    def __str__(self):
        return f"CBC Body {self.id}"


class CbcReport(models.Model):

    cbc_body = models.ForeignKey(CbcBody, on_delete=models.CASCADE)

    country_code = models.CharField(max_length=2)

    unrelated_revenue = models.DecimalField(max_digits=18, decimal_places=3, default=0)

    related_revenue = models.DecimalField(max_digits=18, decimal_places=3, default=0)

    total_revenue = models.DecimalField(max_digits=18, decimal_places=3, default=0)

    profit_loss = models.DecimalField(max_digits=18, decimal_places=3, default=0)

    tax_paid = models.DecimalField(max_digits=18, decimal_places=3, default=0)

    tax_accrued = models.DecimalField(max_digits=18, decimal_places=3, default=0)

    capital = models.DecimalField(max_digits=18, decimal_places=3, default=0)

    earnings = models.DecimalField(max_digits=18, decimal_places=3, default=0)

    employees = models.IntegerField(default=0)

    assets = models.DecimalField(max_digits=18, decimal_places=3, default=0)

    def __str__(self):
        return f"Report {self.country_code}"


class Summary(models.Model):

    report = models.ForeignKey(CbcReport, on_delete=models.CASCADE)

    entity_name = models.CharField(max_length=200)

    country_code = models.CharField(max_length=2)

    activity = models.CharField(max_length=200)

    def __str__(self):
        return self.entity_name