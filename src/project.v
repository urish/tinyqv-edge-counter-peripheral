/*
 * Copyright (c) 2024 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_edge_counter (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  // All output pins must be assigned. If not used, assign to 0.
  assign uio_oe = ui_in[2] ? 8'hFF : 8'h00;

  tqvp_edge_counter edge_counter_inst (
      .clk(clk),
      .rst_n(rst_n),
      .ui_in(ui_in),
      .uo_out(uo_out),
      .address(ui_in[7:4]),
      .data_write(ui_in[3]),
      .data_in(uio_in),
      .data_out(uio_out)
  );

  // List all unused inputs to prevent warnings
  wire _unused = &{ena, 1'b0};

endmodule
