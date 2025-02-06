// constants.ts is a file for all the CONSTANTS we can use in the Frontend application

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
    label: "Prédiction",
    icon: "pi pi-chart-bar",
    route: "/prediction",
  },
  {
    label: "Contact",
    icon: "pi pi-envelope",
    route: "/contact",
  },
]
