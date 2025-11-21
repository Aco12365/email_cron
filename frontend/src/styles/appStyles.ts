// src/styles/appStyles.ts
import { makeStyles } from "@fluentui/react-components";

export const useAppStyles = makeStyles({
  root: {
    width: "180vh",
    minHeight: "100vh",
    margin: 0,
    padding: "40px 16px",
    display: "flex",
    justifyContent: "center",
    alignItems: "flex-start",
    background: "linear-gradient(180deg, #ffffff 0%, #f7f8ff 70%, #f0f4ff 100%)",
  },

  container: {
    width: "100%",
    maxWidth: "1100px",
  },

  titleWrapper: {
    display: "flex",
    flexDirection: "column",
    textAlign: "center",
    marginBottom: "32px",
  },

  subtitle: {
    marginTop: "8px",
    fontSize: "16px",
    color: "#666",
  },

  card: {
    width: "100%",
    padding: "20px",
    borderRadius: "14px",
    boxShadow: "0 12px 30px rgba(0,0,0,0.08)",
    background: "#ffffff",
  },

  formGrid: {
    display: "flex",
    flexDirection: "column",
    gap: "18px",
    marginTop: "10px",
  },

  recipientsRow: {
    display: "flex",
    gap: "10px",
    alignItems: "center",
  },

  tagGroupWrapper: {
    marginTop: "8px",
  },

  footer: {
    marginTop: "28px",
    display: "flex",
    alignItems: "center",
    gap: "12px",
    flexWrap: "wrap",
  },

  statusText: {
    minHeight: "22px",
    fontWeight: 500,
  },
});
