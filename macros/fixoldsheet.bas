Sub CompareAndReplace()
    Dim ws As Worksheet
    Dim lastRow As Long, i As Long

    Application.ScreenUpdating = False ' Turn off screen updating to speed up the macro.

    For Each ws In ThisWorkbook.Sheets
        With ws
            lastRow = .Cells(.Rows.Count, "O").End(xlUp).Row ' Find the last row with data in column O.

            For i = 2 To lastRow ' Iterate through each row.
                If Not IsEmpty(.Cells(i, "O").Value) Then ' Check if column O is not empty.
                    If .Cells(i, "AB").Value > .Cells(i, "O").Value Then
                        .Cells(i, "AB").Value = 1 ' Replace AB with 1 if AB > O.
                    Else
                        .Cells(i, "AB").Value = 0 ' Replace AB with 0 otherwise.
                    End If
                Else
                    .Cells(i, "AB").Value = "NAN" ' Fill AB with "NAN" if O is empty.
                End If
            Next i
        End With
    Next ws

    Application.ScreenUpdating = True ' Turn on screen updating.
End Sub
