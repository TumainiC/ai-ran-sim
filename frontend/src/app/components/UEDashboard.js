import { formatBitrate } from "../utils/formatUtils";

export default function UEDashboard({ simulationState }) {
  if (
    simulationState === null ||
    simulationState.base_station === null ||
    simulationState.UE_list === null
  ) {
    return <div>Simulation Status Not Available Yet.</div>;
  }

  return (
    <div className="gap-1">
      <div className="divider">UE Dashboard</div>
      <div className="overflow-x-auto overflow-y-auto max-h-[1000px]">
        <table className="table table-xs table-pin-rows table-pin-cols">
          <thead>
            <tr>
              <th>UE IMSI</th>
              <td>Current Cell</td>
              <td>Position</td>
              <td>Slice / QoS</td>
              <td>Downlink Bitrate</td>
              <td>Downlink Signals</td>
              <td>Downlink SINR / CQI</td>
              <td>Downlink MCS Index / MCS Data</td>
            </tr>
          </thead>
          <tbody>
            {simulationState.UE_list.map((ue) => (
              <tr key={ue.ue_imsi}>
                <th>{ue.ue_imsi}</th>
                <td>{ue.current_cell}</td>
                <td>
                  X: {ue.vis_position_x}, Y: {ue.vis_position_y}
                </td>
                <td>
                  Slice: {ue.slice_type} <br /> 5QI: {ue.qos_profile["5QI"]}{" "}
                  <br /> GBR_DL: {formatBitrate(ue.qos_profile["GBR_DL"])}{" "}
                  <br /> GBR_UL: {formatBitrate(ue.qos_profile["GBR_UL"])}
                </td>
                <td>{formatBitrate(ue.downlink_bitrate)}</td>
                <td>
                  {Object.keys(ue.downlink_received_power_dBm_dict).map(
                    (cell_id) => {
                      const frequency_priority =
                        ue.downlink_received_power_dBm_dict[cell_id]
                          .frequency_priority;

                      const received_power_dBm =
                        ue.downlink_received_power_dBm_dict[cell_id]
                          .received_power_dBm;
                      return (
                        <div key={cell_id}>
                          {cell_id}: freq priority: {frequency_priority} signal
                          power: {received_power_dBm} dBm
                        </div>
                      );
                    }
                  )}
                </td>
                <td>
                  {ue.downlink_sinr} dB <br /> CQI: {ue.downlink_cqi}
                </td>
                <td>
                  MCS Index: {ue.downlink_mcs_index} <br />{" "}
                  {JSON.stringify(ue.downlink_mcs_data)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
