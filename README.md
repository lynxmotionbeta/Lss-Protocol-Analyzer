
  # LSS Bus Protocol Analyzer
  
## RobotShop Lynxmotion LSS devices

This Saleae extension is for analyzing the serial bus protocol traffic of Lynxmotion LSS servos and other devices.

1. Attach 2 Logic8/16 channel inputs to the LSS RX and TX lines of the LSS bus
2. Open Saleae Logic Software and add Async serial to each of the channels
2. Verify that serial data from the LSS bus is being captured
3. Add this extension to each of the channels using the Async Serial as input to this extension

You should immediately see the AsyncSerial data being translated into LSS packets.

## Analyzing only error packets

It may be helpful to only process packets that are not successful. Edit the LSS Bus Protocol Analyzer settings
and select "Errors Only" in the Display Level selector.

## Search filter for Errors Only

Another way to analyze errors is to enter "error" in the table's search box. This will limit the table to only
errors and you can click on a table row to inspect the serial bits in the graph window.

  