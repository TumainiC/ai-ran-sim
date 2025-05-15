export default function BaseStationDashboard({ simulationState }) {
  if (
    simulationState === null ||
    simulationState.base_station === null ||
    simulationState.UE_list === null
  ) {
    return <div>Simulation Status Not Available Yet.</div>;
  }

  return (
    <div className="gap-1">
      {/* bs_id, cell_id, carrier_frequency_MHz, allocated_prb/max_prb/load, prb_ue_allocation_dict */}
      <div className="grid grid-cols-2 gap-2 items-center px-6">
        {simulationState.base_stations.map((bs) => (
          <div
            key={bs.bs_id + "_bs"}
            className="border-1 border-gray-300 p-2 rounded-md"
          >
            <div className="text-center">Base Station: {bs.bs_id}</div>
            {bs.cell_list.map((cell) => (
              <div key={cell.cell_id + "_cell"}>
                <div className="divider">Cell: {cell.cell_id}</div>
                <div className="grid grid-cols-2 gap-2 items-center">
                  <div>
                    Carrier Freq. <br /> / BW.{" "}
                  </div>
                  <div>
                    {cell.carrier_frequency_MHz} / {cell.bandwidth_Hz / 1e6} MHz
                  </div>
                  <div>
                    Alloc. / Max Downlink PRB <br />
                  </div>
                  <div>
                    {cell.allocated_dl_prb} / {cell.max_dl_prb}
                  </div>
                  <div>
                    Alloc. / Max Uplink PRB <br />
                  </div>
                  <div>
                    {cell.allocated_ul_prb} / {cell.max_ul_prb}
                  </div>
                  <div>Downlink / Up Load</div>
                  <div className="stats">
                    <div className="stat">
                      <div className="stat-value">
                        {(cell.current_dl_load * 100).toFixed(1)} % /
                        {(cell.current_ul_load * 100).toFixed(1)} %
                      </div>
                    </div>
                  </div>
                  <div>Cell Radius</div>
                  <div>{cell.vis_cell_radius * 2} m</div>
                  <div>UE served</div>
                  <div>{Object.keys(cell.prb_ue_allocation_dict).length}</div>
                </div>
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}
