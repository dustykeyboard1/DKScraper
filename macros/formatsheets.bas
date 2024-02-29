Sub AutoFitAndSortSheets()
    Dim ws As Worksheet
    Dim lastRow As Long

    Application.ScreenUpdating = False ' Turn off screen updating to speed up the macro.
    
    For Each ws In ThisWorkbook.Sheets
        With ws
            .Cells.EntireColumn.AutoFit ' Auto fit all columns.
            
            lastRow = .Cells(.Rows.Count, "F").End(xlUp).Row ' Find the last row with data in column F.
            
            ' Check if there is more than one row of data to sort.
            If lastRow > 1 Then
                ' Sort the data based on column F values.
                With .Sort
                    .SortFields.Clear
                    .SortFields.Add Key:=Range("F1:F" & lastRow), _
                        SortOn:=xlSortOnValues, Order:=xlAscending, DataOption:=xlSortNormal
                    .SetRange Range("A1:Z" & lastRow) ' Adjust the range "A1:Z" as per your data range.
                    .Header = xlYes ' Assuming the first row is the header row.
                    .Apply
                End With
            End If
        End With
    Next ws

    Application.ScreenUpdating = True ' Turn on screen updating.
End Sub
