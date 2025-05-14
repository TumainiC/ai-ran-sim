export default function LogDashboard({ simulationState }) {
  if (simulationState === null || simulationState.logs === null) {
    return <div>No simulation logs to show.</div>;
  }

  return (
    <div className="gap-1">
      <div className="divider">Logs</div>
      <div className="log-container">
        {simulationState.logs.map((log, index) => (
          <div key={"log_" + index} className="log">
            {log}
          </div>
        ))}
      </div>
    </div>
  );
}
