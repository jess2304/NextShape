<script setup lang="ts">
import NsButton from "@/components/ui/NsButton.vue"

const steps = [
  {
    number: "01",
    icon: "pi pi-chart-bar",
    title: "Comprendre",
    text: "Un premier repère avec votre IMC.",
    to: "/calculatrice-imc",
  },
  {
    number: "02",
    icon: "pi pi-calculator",
    title: "Ajuster",
    text: "Des besoins caloriques selon votre profil.",
    to: "/calculatrice-calories",
  },
  {
    number: "03",
    icon: "pi pi-history",
    title: "Avancer",
    text: "Vos mesures réunies dans un historique.",
    to: "/historique",
  },
]
</script>

<template>
  <div class="home">
    <section class="home-hero" aria-labelledby="home-title">
      <div class="home-hero__copy">
        <p class="home-kicker">
          <span aria-hidden="true" />Nutrition & bien-être, à votre rythme
        </p>
        <h1 id="home-title">
          Des repères clairs.<br />Des habitudes<br /><span
            >qui vous ressemblent.</span
          >
        </h1>
        <p class="home-hero__description">
          Comprenez vos besoins, ajustez votre alimentation et gardez le fil de
          vos progrès. NextShape vous aide à faire le prochain pas.
        </p>
        <div class="home-hero__actions">
          <NsButton
            as="router-link"
            to="/calculatrice-imc"
            label="Calculer mon IMC"
            icon="pi pi-arrow-right"
            iconPos="right"
          />
          <NsButton
            as="router-link"
            to="/calculatrice-calories"
            label="Estimer mes calories"
            outlined
          />
        </div>
        <p class="home-hero__note">
          <i class="pi pi-check-circle" aria-hidden="true" />Le calcul de l’IMC
          est accessible sans compte.
        </p>
      </div>

      <div class="home-journey">
        <div class="home-journey__top">
          <span>LA MÉTHODE NEXTSHAPE</span
          ><i class="pi pi-sun" aria-hidden="true" />
        </div>
        <h2>Pas besoin de tout changer.<br />Commencez par vous.</h2>
        <p>Quelques informations.<br />Des repères pour la suite.</p>
        <div class="journey-list">
          <RouterLink
            v-for="step in steps"
            :key="step.number"
            :to="step.to"
            class="journey-item"
          >
            <span class="journey-item__number">{{ step.number }}</span>
            <span class="journey-item__copy"
              ><strong>{{ step.title }}</strong
              ><span>{{ step.text }}</span></span
            >
            <i class="pi pi-arrow-up-right" aria-hidden="true" />
          </RouterLink>
        </div>
        <div class="home-journey__footer">
          <span class="journey-mark" aria-hidden="true">n.</span
          ><span>Un pas à la fois,<br />dans la bonne direction.</span>
        </div>
      </div>
    </section>

    <section class="home-tools" aria-labelledby="tools-title">
      <div class="home-tools__heading">
        <p class="ns-eyebrow">L’essentiel, simplement</p>
        <h2 id="tools-title">Votre quotidien.<br />Un peu plus clair.</h2>
      </div>
      <div class="home-tools__grid">
        <article>
          <span class="home-tool-icon pi pi-sliders-h" aria-hidden="true" />
          <h3>Des repères personnels</h3>
          <p>
            Estimez vos besoins selon votre activité et votre objectif, à partir
            de vos informations.
          </p>
          <RouterLink to="/calculatrice-calories"
            >Découvrir le calcul
            <i class="pi pi-arrow-right" aria-hidden="true"
          /></RouterLink>
        </article>
        <article>
          <span class="home-tool-icon pi pi-calendar" aria-hidden="true" />
          <h3>Une vue sur la durée</h3>
          <p>
            Retrouvez les mesures que vous enregistrez. Votre historique vous
            aide à garder le cap.
          </p>
          <RouterLink to="/historique"
            >Retrouver mon suivi
            <i class="pi pi-arrow-right" aria-hidden="true"
          /></RouterLink>
        </article>
        <article>
          <span class="home-tool-icon pi pi-sparkles" aria-hidden="true" />
          <h3>Des idées pour vos repas</h3>
          <p>
            Préparez un programme nutritionnel en tenant compte de vos
            préférences alimentaires.
          </p>
          <RouterLink to="/evolution"
            >Explorer mon programme
            <i class="pi pi-arrow-right" aria-hidden="true"
          /></RouterLink>
        </article>
      </div>
    </section>
  </div>
</template>

<style scoped>
.home-hero {
  display: grid;
  grid-template-columns: 1.15fr 1fr;
  gap: clamp(2.5rem, 6vw, 6rem);
  align-items: center;
  padding: 0.75rem 0 4.5rem;
}
.home-kicker {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-size: 0.72rem;
  font-weight: 500;
  color: var(--ns-primary);
  margin: 0 0 1.8rem;
}
.home-kicker > span {
  width: 0.4rem;
  height: 0.4rem;
  border-radius: 50%;
  background: #729a63;
}
.home-hero h1 {
  font-size: clamp(2.35rem, 4.5vw, 3.65rem);
  line-height: 1.1;
  font-weight: 550;
  letter-spacing: -0.065em;
  margin: 0;
}
.home-hero h1 > span {
  color: var(--ns-primary);
}
.home-hero__description {
  color: var(--ns-muted);
  line-height: 1.8;
  font-size: 0.96rem;
  max-width: 29rem;
  margin: 1.6rem 0 2rem;
}
.home-hero__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}
.home-hero__actions :deep(.p-button) {
  font-size: 0.8rem;
  min-height: 3rem;
}
.home-hero__note {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--ns-muted);
  font-size: 0.7rem;
  margin: 1.2rem 0 0;
}
.home-hero__note .pi {
  color: var(--ns-primary);
  font-size: 0.8rem;
}
.home-journey {
  background: var(--ns-primary);
  color: #fff;
  border-radius: 16px;
  padding: clamp(1.75rem, 3vw, 2.5rem);
  position: relative;
  overflow: hidden;
}
.home-journey::before {
  content: "";
  position: absolute;
  width: 17rem;
  height: 17rem;
  border: 1px solid #ffffff12;
  border-radius: 50%;
  top: -11rem;
  right: -4rem;
  box-shadow: 0 0 0 2.5rem #ffffff04, 0 0 0 5rem #ffffff03;
  pointer-events: none;
}
.home-journey__top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #c4d4c6;
  font-size: 0.6rem;
  letter-spacing: 0.14em;
  font-weight: 500;
}
.home-journey__top .pi {
  font-size: 1.5rem;
}
.home-journey h2 {
  font-size: clamp(1.35rem, 2.5vw, 1.75rem);
  letter-spacing: -0.04em;
  line-height: 1.3;
  font-weight: 500;
  margin: 2rem 0 0.75rem;
}
.home-journey > p {
  font-size: 0.8rem;
  color: #c3d2c8;
  line-height: 1.75;
  margin: 0 0 1.75rem;
}
.journey-list {
  border-top: 1px solid #ffffff25;
}
.journey-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.15rem 0;
  border-bottom: 1px solid #ffffff25;
  text-decoration: none;
  color: white;
}
.journey-item:hover .journey-item__copy strong {
  text-decoration: underline;
  text-underline-offset: 0.2em;
}
.journey-item:focus-visible {
  outline-color: #d5e6cb;
}
.journey-item__number {
  color: #c2d9b5;
  font-size: 0.7rem;
  align-self: start;
  margin-top: 0.25rem;
  font-variant-numeric: tabular-nums;
}
.journey-item__copy {
  display: grid;
  gap: 0.3rem;
  flex: 1;
}
.journey-item__copy strong {
  font-size: 0.875rem;
  font-weight: 550;
}
.journey-item__copy > span {
  font-size: 0.7rem;
  color: #c3d2c8;
}
.journey-item > .pi {
  font-size: 0.7rem;
  color: #c2d9b5;
}
.home-journey__footer {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: 1.75rem;
  font-size: 0.65rem;
  line-height: 1.6;
  color: #c3d2c8;
}
.journey-mark {
  width: 2.4rem;
  height: 2.4rem;
  display: grid;
  place-items: center;
  font-size: 1.5rem;
  font-weight: 500;
  letter-spacing: -0.1em;
  border: 1px solid #ffffff30;
  border-radius: 50%;
  color: #d0dfc8;
  padding-right: 0.15rem;
}
.home-tools {
  padding-top: 2.5rem;
  border-top: 1px solid var(--ns-border);
  display: grid;
  grid-template-columns: 0.85fr 3fr;
  gap: 3rem;
}
.home-tools__heading h2 {
  font-size: 1.45rem;
  font-weight: 550;
  letter-spacing: -0.045em;
  line-height: 1.25;
  margin: 0;
}
.home-tools__grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 2rem;
}
.home-tool-icon {
  display: grid;
  place-items: center;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 8px;
  color: var(--ns-primary);
  background: var(--ns-sage);
  font-size: 1rem;
}
.home-tools h3 {
  margin: 1rem 0 0.65rem;
  font-size: 0.875rem;
}
.home-tools article p {
  font-size: 0.8rem;
  color: var(--ns-muted);
  line-height: 1.8;
  margin: 0 0 1rem;
}
.home-tools article a {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.72rem;
  font-weight: 600;
  text-decoration: none;
}
.home-tools article a:hover {
  text-decoration: underline;
}
.home-tools article a .pi {
  font-size: 0.6rem;
}
@media (max-width: 1050px) {
  .home-hero {
    gap: 2.25rem;
  }
  .home-tools {
    grid-template-columns: 1fr;
    gap: 2rem;
  }
  .home-tools__heading h2 br {
    display: none;
  }
}
@media (max-width: 700px) {
  .home-hero {
    grid-template-columns: 1fr;
    gap: 2.5rem;
    padding: 0.5rem 0 2.5rem;
  }
  .home-hero h1 {
    font-size: clamp(2.35rem, 7.5vw, 3.5rem);
  }
  .home-hero__description {
    max-width: 34rem;
  }
  .home-tools__grid {
    grid-template-columns: 1fr;
    gap: 0;
  }
  .home-tools article {
    padding: 1.5rem 0;
    border-bottom: 1px solid var(--ns-border);
  }
  .home-tools article:first-child {
    padding-top: 0;
  }
  .home-tools article:last-child {
    border-bottom: 0;
    padding-bottom: 0;
  }
  .home-tools article p {
    max-width: 30rem;
  }
  .home-kicker {
    margin-bottom: 1.5rem;
  }
}
@media (max-width: 380px) {
  .home-hero__actions {
    flex-direction: column;
  }
  .home-journey {
    padding: 1.5rem;
  }
}
</style>
