// constants.ts est un fichier présentant toutes les constantes du projet.

export const NAVBAR_ELEMENTS = [
  {
    label: "Calculatrice",
    icon: "pi pi-calculator",
    items: [
      {
        label: "Calculatrice d'IMC",
        route: "/calculatrice-imc",
      },
      {
        label: "Calculatrice de calories",
        route: "/calculatrice-calories",
      },
    ],
  },
  {
    label: "Historique",
    icon: "pi pi-history",
    route: "/historique",
  },
  {
    label: "Évolution",
    icon: "pi pi-chart-line",
    route: "/evolution",
  },
  {
    label: "Contact",
    icon: "pi pi-envelope",
    route: "/contact",
  },
]

// Presentation texts for home
export const TITLE = "Transforme ton corps, contrôle tes calories !"
export const SUBTITLE =
  "NextShape t'aide à suivre ton évolution physique avec une précision inégalée. En quelques clics, tu peux <strong>calculer ton IMC</strong> à tout moment, gratuitement et sans inscription. Pour aller plus loin et <strong>connaître tes besoins caloriques personnalisés</strong>, il te suffit de créer un compte. C'est rapide, sécurisé, et ça te donne accès à des recommandations sur mesure."
export const PRESENTATION_TEXT =
  "<strong>Tu cherches un moyen simple et efficace de suivre ton évolution physique ?</strong><br><br> NextShape est là pour t'aider à calculer ton IMC, déterminer tes besoins caloriques et visualiser tes progrès au fil du temps. <br><br>Que tu sois en phase de perte de poids, de prise de masse ou simplement curieux de voir comment ton corps évolue, cette plateforme te permet d'avoir une vue d'ensemble claire et détaillée de tes données. <br><br>Pas d'algorithmes compliqués ni de recommandations approximatives : juste des calculs précis et des graphiques pour t'aider à mieux comprendre ton évolution et ajuster ton mode de vie en fonction de tes propres objectifs."

export const GENDER = [
  {
    label: "Homme",
    value: "H",
  },
  {
    label: "Femme",
    value: "F",
  },
]

export const ACTIVITY_LEVELS = [
  { label: "Sédentaire", value: "sedentaire" },
  { label: "Léger", value: "leger" },
  { label: "Modéré", value: "modere" },
  { label: "Intense", value: "intense" },
  { label: "Très intense", value: "tres_intense" },
]

export const ACTIVITY_DESCRIPTIONS: Record<string, string> = {
  sedentaire: "Aucune activité physique ou travail de bureau.",
  leger: "Marche ou activité légère 1 à 2 fois/semaine.",
  modere: "Sport ou activité modérée 3 à 5 fois/semaine.",
  intense: "Exercice quotidien ou activité physique intense.",
  tres_intense: "Entraînement intensif ou travail physique très exigeant.",
}

export const GOALS = [
  { label: "Perte de poids", value: "perte" },
  { label: "Maintien", value: "maintien" },
  { label: "Prise de masse", value: "prise" },
]
