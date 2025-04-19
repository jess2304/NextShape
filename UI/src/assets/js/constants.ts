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
  "NextShape t'aide à suivre ton évolution physique avec une précision inégalée."
export const PRESENTATION_TEXT =
  "Tu cherches un moyen simple et efficace de suivre ton évolution physique ? NextShape est là pour t'aider à calculer ton IMC, déterminer tes besoins caloriques et visualiser tes progrès au fil du temps. Que tu sois en phase de perte de poids, de prise de masse ou simplement curieux de voir comment ton corps évolue, cette plateforme te permet d'avoir une vue d'ensemble claire et détaillée de tes données. Pas d'algorithmes compliqués ni de recommandations approximatives : juste des calculs précis et des graphiques pour t'aider à mieux comprendre ton évolution et ajuster ton mode de vie en fonction de tes propres objectifs."
