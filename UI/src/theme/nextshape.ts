import { definePreset } from "@primevue/themes"
import Aura from "@primevue/themes/aura"

// PrimeVue keeps keyboard, focus and overlay behavior; NextShape owns the palette.
export default definePreset(Aura, {
  primitive: {
    borderRadius: {
      none: "0",
      xs: "4px",
      sm: "6px",
      md: "8px",
      lg: "12px",
      xl: "16px",
    },
  },
  semantic: {
    primary: {
      50: "#f0f5f0",
      100: "#e7eee7",
      200: "#cbdcd0",
      300: "#a3c2af",
      400: "#709b82",
      500: "#3c7059",
      600: "#2b604c",
      700: "#1d4d40",
      800: "#183f34",
      900: "#12332a",
      950: "#0b211c",
    },
    focusRing: {
      width: "2px",
      style: "solid",
      color: "{primary.500}",
      offset: "3px",
    },
    formField: {
      paddingX: ".875rem",
      paddingY: ".75rem",
      borderRadius: "8px",
      focusRing: {
        width: "3px",
        style: "solid",
        color: "{primary.100}",
        offset: "0",
      },
    },
    colorScheme: {
      light: {
        surface: {
          0: "#ffffff",
          50: "#fafaf7",
          100: "#f6f5f0",
          200: "#e2e7df",
          300: "#cbd3c9",
          400: "#8d9a90",
          500: "#69766f",
          600: "#4f5e55",
          700: "#34453b",
          800: "#202b26",
          900: "#16231b",
          950: "#0b150f",
        },
        primary: {
          color: "{primary.700}",
          contrastColor: "#ffffff",
          hoverColor: "{primary.800}",
          activeColor: "{primary.900}",
        },
        text: {
          color: "{surface.800}",
          hoverColor: "{surface.900}",
          mutedColor: "{surface.500}",
          hoverMutedColor: "{surface.600}",
        },
        highlight: {
          background: "{primary.100}",
          focusBackground: "{primary.200}",
          color: "{primary.800}",
          focusColor: "{primary.900}",
        },
        formField: {
          borderColor: "{surface.300}",
          hoverBorderColor: "{primary.400}",
          color: "{surface.800}",
          shadow: "none",
        },
        content: { borderColor: "#dee4dd" },
      },
    },
  },
  components: {
    button: {
      root: {
        borderRadius: "8px",
        paddingX: "1.125rem",
        paddingY: ".75rem",
        gap: ".5rem",
        label: { fontWeight: "600" },
      },
    },
    dialog: {
      root: { borderRadius: "16px" },
      header: { padding: "1.5rem" },
      content: { padding: "0 1.5rem 1.5rem" },
      footer: { padding: "0 1.5rem 1.5rem", gap: ".75rem" },
    },
    card: {
      root: {
        shadow: "0 2px 8px rgba(29, 77, 64, .025)",
        borderRadius: "16px",
      },
    },
    datatable: {
      headerCell: { padding: "1rem", background: "{surface.50}" },
      bodyCell: { padding: "1rem" },
    },
    tabs: {
      tablist: { background: "transparent" },
      tabpanel: { background: "transparent", padding: "1.5rem 0 0" },
    },
    toast: { root: { width: "24rem", borderRadius: "12px" } },
  },
})
