from django.db import models
from django.utils import timezone  # Import para usar timezone.now como valor padrão

class Processo(models.Model):
    numero_processo = models.CharField(max_length=50, unique=True)
    autor = models.CharField(max_length=100)
    reu = models.CharField(max_length=100)
    data_ajuizamento = models.DateTimeField(default=timezone.now)  # Definindo timezone.now como valor padrão
    vara = models.CharField(max_length=50)
    status = models.CharField(
        max_length=20,
        choices=[('Em Andamento', 'Em Andamento'), ('Concluído', 'Concluído')]
    )
    valor_causa = models.DecimalField(max_digits=10, decimal_places=2)
    data_criacao = models.DateTimeField(auto_now_add=True)  # Data de criação automática

    def __str__(self):
        return f"{self.numero_processo} - {self.autor} vs {self.reu}"
