<script setup lang="ts">
const currentYear = new Date().getFullYear()
</script>

<template>
  <footer class="public-footer">
    <div class="public-footer__inner">
      <p>© {{ currentYear }} NextShape<span> · À votre rythme.</span></p>
      <nav aria-label="Liens de bas de page">
        <RouterLink to="/calculatrice-imc">Calculer mon IMC</RouterLink
        ><RouterLink to="/contact">Nous contacter</RouterLink>
      </nav>
    </div>
  </footer>
</template>

<style scoped>
.public-footer {
  border-top: 1px solid var(--ns-border);
}
.public-footer__inner {
  max-width: 1280px;
  padding: 1.5rem 2.5rem;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  font-size: 0.75rem;
  color: var(--ns-muted);
}
.public-footer p {
  margin: 0;
}
.public-footer nav {
  display: flex;
  gap: 1.5rem;
}
.public-footer a {
  color: var(--ns-muted);
  text-decoration: none;
}
.public-footer a:hover {
  color: var(--ns-primary);
  text-decoration: underline;
}
@media (max-width: 640px) {
  .public-footer__inner {
    padding: 1.5rem 1rem;
    flex-direction: column;
    align-items: start;
  }
}
</style>
