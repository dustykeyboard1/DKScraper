Sub CopyRowsWithTakeIncludingHeaders()
    Dim sourceSheet As Worksheet, destinationSheet As Worksheet
    Dim lastRow As Long, destinationRow As Long
    Dim i As Long

    ' Replace 'Sheet1' with your actual source sheet name
    ' Replace 'Sheet2' with your actual destination sheet name
    Set sourceSheet = ThisWorkbook.Sheets("Sheet1")
    Set destinationSheet = ThisWorkbook.Sheets("Sheet2")
    
    ' Find the last row in column K with data
    lastRow = sourceSheet.Cells(sourceSheet.Rows.Count, "K").End(xlUp).Row
    destinationRow = 2 ' Start copying rows to the second row in the destination sheet
    
    ' Copy headers from the first row of the source sheet to the first row of the destination sheet
    sourceSheet.Rows(1).Copy Destination:=destinationSheet.Rows(1)
    
    ' Loop through each row in the source sheet starting from row 1 or 2 depending on your header row
    For i = 1 To lastRow
        If sourceSheet.Cells(i, "K").Value = "take" Then
            sourceSheet.Rows(i).Copy Destination:=destinationSheet.Rows(destinationRow)
            destinationRow = destinationRow + 1
        End If
    Next i
End Sub



