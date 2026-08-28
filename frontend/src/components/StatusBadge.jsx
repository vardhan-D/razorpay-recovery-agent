function StatusBadge({ status }) {
    const normalizedStatus =
      status || "unknown"
  
    return (
      <span
        className={
          `status-badge status-${normalizedStatus}`
        }
      >
        {normalizedStatus.replaceAll("_", " ")}
      </span>
    )
  }
  
  export default StatusBadge