const zlib = require('zlib');

return $input.all().map(item => {
  // 1. Obtener remitente y asunto
  let fromEmail = '';
  if (item.json.from && item.json.from.value && item.json.from.value.length > 0) {
    fromEmail = item.json.from.value[0].address;
  } else {
    fromEmail = item.json.headers?.from || '';
  }

  const subject = item.json.subject || '';
  const attachments = [];

  if (item.binary) {
    for (const key of Object.keys(item.binary)) {
      const file = item.binary[key];
      const buffer = Buffer.from(file.data, 'base64');
      
      // Obtener la firma de cabecera (Magic Bytes en Hexadecimal)
      const hexHeader = buffer.slice(0, 4).toString('hex');
      let xmlContent = '';
      let diagInfo = '';

      // CASO A: Es un archivo ZIP completo (Cabecera PK.. -> 504b0304)
      if (hexHeader.startsWith('504b0304')) {
        try {
          // Extraer el payload comprimido en formato raw inflate desde el contenedor ZIP
          const fileNameLen = buffer.readUInt16LE(26);
          const extraLen = buffer.readUInt16LE(28);
          const dataStart = 30 + fileNameLen + extraLen;
          const compressedData = buffer.slice(dataStart);
          xmlContent = zlib.inflateRawSync(compressedData).toString('utf-8');
        } catch (e) {
          diagInfo = `Error decodificando contenedor ZIP: ${e.message}`;
        }
      }
      // CASO B: Archivo GZIP estándar (1f8b)
      else if (hexHeader.startsWith('1f8b')) {
        try {
          xmlContent = zlib.gunzipSync(buffer).toString('utf-8');
        } catch (e) {
          diagInfo = `Error GZIP: ${e.message}`;
        }
      }
      // CASO C: ZLIB / Deflate con cabecera (789c, 7801, 78da)
      else if (hexHeader.startsWith('789c') || hexHeader.startsWith('7801') || hexHeader.startsWith('78da')) {
        try {
          xmlContent = zlib.inflateSync(buffer).toString('utf-8');
        } catch (e) {
          diagInfo = `Error Inflate: ${e.message}`;
        }
      }
      // CASO D: XML en texto plano en UTF-8 (Empieza por '<' -> 3c)
      else if (hexHeader.startsWith('3c')) {
        xmlContent = buffer.toString('utf-8');
      }
      // CASO E: Codificación UTF-16 (fffe o feff)
      else if (hexHeader.startsWith('fffe') || hexHeader.startsWith('feff')) {
        xmlContent = buffer.toString('utf16le');
      }
      // CASO F: Raw Deflate sin cabecera zlib
      else {
        try {
          xmlContent = zlib.inflateRawSync(buffer).toString('utf-8');
        } catch (e) {
          diagInfo = 'Formato no reconocido como compresión estándar.';
        }
      }

      // Validación de seguridad: Si no se obtuvo XML válido, devolver los Magic Bytes para diagnóstico
      if (!xmlContent || !xmlContent.includes('<')) {
        xmlContent = `[ERROR_DECODIFICACION] Magic Bytes: ${hexHeader} | Detalle: ${diagInfo}`;
      }

      attachments.push({
        filename: file.fileName || key,
        content: xmlContent
      });
    }
  }

  return {
    json: {
      correo: {
        from: fromEmail,
        subject: subject,
        attachments: attachments
      },
      empresa_id: 1,
      user_id: 1
    }
  };
});



// para separar los adjuntos del correo y llevarlos a json
let results = [];
//let salida = [];

for (item of items) {
    for (key of Object.keys(item.binary)) {
        results.push({
            json: {
                fileName: item.binary[key].fileName
            },
            binary: {
                data: item.binary[key],
            }
        });
    }
}
//salida.push({json: {attachments: results}})
return results;